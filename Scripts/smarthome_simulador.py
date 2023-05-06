# Este script realiza las funciones de registrar datos y gestionar los actuadores simulando cambios en 
# el clima. Por ejemplo: se puede simular un día caloroso de humedad alta o un día frío con mucho viento.

# --- MÓDULOS IMPORTADOS ---
from time import sleep
import requests
from datetime import datetime
from pathlib import Path
from influxdb import InfluxDBClient
import pytz
import pymongo
from soco import SoCo
from gtts import gTTS
import os

# --- VARIABLES Y MÉTODOS A USAR ---
valor_simulacion = 0.0

# API:
dir = "http://remote:LabSmarthome21@192.168.7.210/scada-remote" # Direccion de la API
parametros_GET = { # Parametros para la conexion a la API
        'm': 'json', # Formato de salida
        'r': 'grp', # Request
        'fn': 'getvalue', # Función a ejecutar
        'alias': '3/1/1' # Dirección del objeto
    }
parametros_POST = { # Parametros para la conexion a la API
    'm': 'json', # Formato de salida
    'r': 'grp', # Request
    'fn': 'write', # Función a ejecutar
    'alias': '0/0/0', # Dirección del objeto
    'value': '' # Nuevo valor del objeto
}
def GET_datos(parametros): # Conexion y peticion a la API
    r = requests.get(url=dir, params=parametros)
    return r.json()
def POST_datos(parametros):
    r = requests.post(url=dir, params=parametros)
    print(r.status_code)
    print(r.json())

# Sonos
def reproducir_audio(mensaje):
    sonos = SoCo('192.168.7.12')
    sonos.status_light = True
    sonos.volume = 30
    tts = gTTS(mensaje, lang='es')
    tts.save('mensaje_audio.mp3')
    sonos.play_uri("mensaje_audio.mp3")
    os.remove("mensaje_audio.mp3")

# --- CONSULTAS AL USUARIO ---
opcion = input("Activar control de temperatura (True/False): ")
baliza_temp = bool(opcion)

# --- PROGRAMA PRINCIPAL ---
while (True):

    # PARTE 1: RECOGIDA DE DATOS

    # Datos que se recogen de la SmartHome
    tempInterior = GET_datos(parametros_GET)
    tempInterior += 0.0
    parametros_GET['alias'] = '3/2/5' # Alias del siguiente sensor
    tempExterior = GET_datos(parametros_GET)
    tempExterior += 0.0 # Para evitar valores enteros
    tempExterior += valor_simulacion
    if valor_simulacion <= 10.0:
        valor_simulacion += 1.0
    parametros_GET['alias'] = '3/2/1'
    CO2 = GET_datos(parametros_GET)
    CO2 += 0.0 # Para evitar valores enteros
    parametros_GET['alias'] = '3/2/2'
    humedadInterior = GET_datos(parametros_GET)
    humedadInterior += 0.0 # Para evitar valores enteros
    parametros_GET['alias'] = '3/2/4'
    velocidadViento =  GET_datos(parametros_GET)
    velocidadViento += 0.0 # Para evitar valores enteros
    parametros_GET['alias'] = '3/2/6'
    luxExterior = GET_datos(parametros_GET)
    luxExterior += 0.0 # Para evitar valores enteros
    parametros_GET['alias'] = '3/2/10'
    lluvia = GET_datos(parametros_GET)

    # PARTE 2: ENVIO DE DATOS A BD INFLUX Y A BD MONGO

    # Configurar conexiones...
    conexInfluxDB = InfluxDBClient('localhost', 8086, 'admin', 'admin', 'smarthome') # ... a InfluxDB
    conexMongoDB = pymongo.MongoClient("mongodb://localhost:27017/") # ... a mongoDB
    mongoDBActual = conexMongoDB["smarthome"]
    mongoColecActual = mongoDBActual["tempInterior"]

    # La zona horaria sera UTC para evitar problemas de incompatibilidad con Grafana
    zonaHoraria = pytz.timezone('UTC') 
    now = datetime.now(zonaHoraria)

    # Se configura un payload, carga util, para cada una de las medidas que se realizan y se actualiza la base de datos
    # Temperatura
    json_payload = []
    json_data = {
        "measurement": "tempInterior",
        "time": now,
        "fields": {
            'value': tempInterior
        }
    }
    json_payload.append(json_data)
    # Se debe insertar ya en la mongoDB y cambiar la coleccion
    mongoColecActual.insert_one(json_data)
    mongoColecActual = mongoDBActual["tempExterior"]
    json_data = {
        "measurement": "tempExterior",
        "time": now,
        "fields": {
            'value': tempExterior
        }
    }
    json_payload.append(json_data)
    mongoColecActual.insert_one(json_data)
    mongoColecActual = mongoDBActual["CO2"]

    # Contaminación
    json_data = {
        "measurement": "CO2",
        "time": now,
        "fields": {
            'value': CO2
        }
    }
    json_payload.append(json_data)
    mongoColecActual.insert_one(json_data)
    mongoColecActual = mongoDBActual["humedadInterior"]

    # Humedad
    json_data = {
        "measurement": "humedadInterior",
        "time": now,
        "fields": {
            'value': humedadInterior
        }
    }
    json_payload.append(json_data)
    mongoColecActual.insert_one(json_data)
    mongoColecActual = mongoDBActual["velocidadViento"]

    # Velocidad del viento
    json_data = {
        "measurement": "velocidadViento",
        "time": now,
        "fields": {
            'value': velocidadViento
        }
    }
    json_payload.append(json_data)
    mongoColecActual.insert_one(json_data)
    mongoColecActual = mongoDBActual["luxExterior"]

    # Luminosidad
    json_data = {
        "measurement": "luxExterior",
        "time": now,
        "fields": {
            'value': luxExterior
        }
    }
    json_payload.append(json_data)
    mongoColecActual.insert_one(json_data)
    mongoColecActual = mongoDBActual["lluvia"]

    # Lluvia
    json_data = {
        "measurement": "lluvia",
        "time": now,
        "fields": {
            'value': lluvia
        }
    }
    json_payload.append(json_data)
    conexInfluxDB.write_points(json_payload)
    mongoColecActual.insert_one(json_data)

    # PARTE 3: EXPORTACION DE DATOS EN TXT

    now = datetime.now()
    fecha = now.strftime('%d-%m-%Y')
    hora = now.strftime('%H:%M')
    # Debemos comprobar si existe el archivo para añadir la cabecera o no
    fileObj = Path('C:\\Users\\TFG3\\Desktop\\David TFG\\txtLogs\\' + fecha + '.txt')
    if(fileObj.is_file()):
        f = open('C:\\Users\\TFG3\\Desktop\\David TFG\\txtLogs\\' + fecha+'.txt', 'a')
        f.write(hora + '\t%2.1f\t%2.1f\t%3.2f\t%d\t%d\t%4.2f\t%d\n' % (tempInterior, tempExterior, CO2, humedadInterior, velocidadViento, luxExterior, not lluvia))
        f.close
    else:
        print('No existe el fichero')
        f = open('C:\\Users\\TFG3\\Desktop\\David TFG\\txtLogs\\' + fecha+'.txt', 'w')
        f.write('HORA\tTEMPERATURA INT.\tTEMPERATURA EXT.\tCO2\tHUMEDAD INT.\tVEL. VIENTO\tLUMINOSIDAD EXT.\tLLUVIA\n')
        f.write(hora + '\t%2.1f\t%2.1f\t%3.2f\t%d\t%d\t%4.2f\t%d\n' % (tempInterior, tempExterior, CO2, humedadInterior, velocidadViento, luxExterior, not lluvia))
        f.close

    # PARTE 4: GESTOR DEL SIMULADOR

    # Gestor de confort
    if (baliza_temp):
        # Recogida de datos
        parametros_GET['alias'] = '2/3/7'
        altura_ventana = GET_datos(parametros_GET)
        if (altura_ventana < 100):
            print("La ventana está abierta")
        else:
            print("La ventana está abierta")
        print("Temperatura interior: " + str(tempInterior))
        print("Temperatura exterior: " + str(tempExterior))

        # Gestión de cada caso
        if ((tempInterior < 20) and (tempExterior > tempInterior) and (altura_ventana==100)):
            print("Temperatura baja en el interior, abriendo ventanas.")
            #reproducir_audio("Temperatura baja en el interior, abriendo ventanas.")
            parametros_POST['alias'] = '2/3/5'
            parametros_POST['value'] = 0
            POST_datos(parametros_POST)
        if ((tempInterior < 20) and (tempExterior > tempInterior) and (altura_ventana<100)):
            print("Temperatura baja en el interior y exterior, cerrando ventanas.")
            #reproducir_audio("Temperatura baja en el interior y exterior, cerrando ventanas.")
            parametros_POST['alias'] = '2/3/5'
            parametros_POST['value'] = 1
            POST_datos(parametros_POST)
        if ((tempInterior > 25) and (tempExterior > tempInterior) and (altura_ventana<100)):
            print("Temperatura alta en el interior y exterior, cerrando ventanas.")
            #reproducir_audio("Temperatura alta en el interior y exterior, cerrando ventanas.")
            parametros_POST['alias'] = '2/3/5'
            parametros_POST['value'] = 1
            POST_datos(parametros_POST)
        if ((tempInterior > 25) and (tempExterior < tempInterior) and (altura_ventana==100)):
            print("Temperatura alta en el interior, abriendo ventanas.")
            #reproducir_audio("Temperatura alta en el interior, abriendo ventanas.")
            parametros_POST['alias'] = '2/3/5'
            parametros_POST['value'] = 0
            POST_datos(parametros_POST)

    print("Datos simulados correctamente: " + str(fecha) + " " + str(hora))
    
    sleep(1 * 15)