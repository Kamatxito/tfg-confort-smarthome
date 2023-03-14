# En este script se realiza todo el proceso de recogida de datos de los sensores a traves de la
# API de la SmartHome. Esos datos se almacenan en dos bases de datos: una tipo temporal, 
# influxDB; y otra tipo no SQL, mongoDB. Por último, también guarda en un fichero de texto una
# copia de todos los datos que recoge

from time import sleep
import requests
from datetime import datetime
from pathlib import Path
from influxdb import InfluxDBClient
import pytz
import pymongo

while (True):

    # PARTE 1: RECOGIDA DE DATOS

    dir = "http://remote:LabSmarthome21@192.168.7.210/scada-remote" # Direccion de la API

    parametros = { # Parametros para la conexion a la API
        'm': 'json', # Formato de salida
        'r': 'grp', # Request
        'fn': 'getvalue', # Función a ejecutar
        'alias': '3/1/1' # Dirección del objeto
    }

    def peticion_datos(parametros): # Conexion y peticion a la API
        r = requests.get(url=dir, params=parametros)
        return r.json()

    # Datos que se recogen de la SmartHome
    tempInterior = peticion_datos(parametros)
    tempInterior += 0.0
    parametros['alias'] = '3/2/5' # Alias del siguiente sensor
    tempExterior = peticion_datos(parametros)
    parametros['alias'] = '3/2/1'
    CO2 = peticion_datos(parametros)
    parametros['alias'] = '3/2/2'
    humedadInterior = peticion_datos(parametros)
    parametros['alias'] = '3/2/4'
    velocidadViento =  peticion_datos(parametros)
    velocidadViento += 0.0 # Para evitar valores enteros
    parametros['alias'] = '3/2/6'
    luxExterior = peticion_datos(parametros)
    parametros['alias'] = '3/2/10'
    lluvia = peticion_datos(parametros)

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
    data = {
        "measurement": "tempInterior",
        "time": now,
        "fields": {
            'value': tempInterior
        }
    }
    json_payload.append(data)
    # Se debe insertar ya en la mongoDB y cambiar la coleccion
    mongoColecActual.insert_one(data)
    mongoColecActual = mongoDBActual["tempExterior"]
    data = {
        "measurement": "tempExterior",
        "time": now,
        "fields": {
            'value': tempExterior
        }
    }
    json_payload.append(data)
    mongoColecActual.insert_one(data)
    mongoColecActual = mongoDBActual["CO2"]

    # Contaminación
    data = {
        "measurement": "CO2",
        "time": now,
        "fields": {
            'value': CO2
        }
    }
    json_payload.append(data)
    mongoColecActual.insert_one(data)
    mongoColecActual = mongoDBActual["humedadInterior"]

    # Humedad
    data = {
        "measurement": "humedadInterior",
        "time": now,
        "fields": {
            'value': humedadInterior
        }
    }
    json_payload.append(data)
    mongoColecActual.insert_one(data)
    mongoColecActual = mongoDBActual["velocidadViento"]

    # Velocidad del viento
    data = {
        "measurement": "velocidadViento",
        "time": now,
        "fields": {
            'value': velocidadViento
        }
    }
    json_payload.append(data)
    mongoColecActual.insert_one(data)
    mongoColecActual = mongoDBActual["luxExterior"]

    # Luminosidad
    data = {
        "measurement": "luxExterior",
        "time": now,
        "fields": {
            'value': luxExterior
        }
    }
    json_payload.append(data)
    mongoColecActual.insert_one(data)
    mongoColecActual = mongoDBActual["lluvia"]

    # Lluvia
    data = {
        "measurement": "lluvia",
        "time": now,
        "fields": {
            'value': lluvia
        }
    }
    json_payload.append(data)
    conexInfluxDB.write_points(json_payload)
    mongoColecActual.insert_one(data)

    # PARTE 3: EXPORTACION DE DATOS EN TXT
    now = datetime.now()
    fecha = now.strftime('%d-%m-%Y')
    hora = now.strftime('%H:%M')
    # Debemos comprobar si existe el archivo para añadir la cabecera o no
    fileObj = Path('C:\\Users\\Smarthome\\Desktop\\David TFG\\txtLogs' + fecha + '.txt')
    if(fileObj.is_file()):
        f = open('C:\\Users\\Smarthome\\Desktop\\David TFG\\txtLogs' + fecha+'.txt', 'a')
        f.write(hora + '\t%2.1f\t%2.1f\t%3.2f\t%d\t%d\t%4.2f\t%d\n' % (tempInterior, tempExterior,CO2, humedadInterior, velocidadViento, luxExterior, not lluvia))
        f.close
    else:
        print('No existe el fichero')
        f = open('C:\\Users\\Smarthome\\Desktop\\David TFG\\txtLogs' + fecha+'.txt', 'w')
        f.write('HORA\tTEMPERATURA INT.\tTEMPERATURA EXT.\tCO2\tHUMEDAD INT.\tVEL. VIENTO\tLUMINOSIDAD EXT.\tLLUVIA\n')
        f.write(hora + '\t%2.1f\t%2.1f\t%3.2f\t%d\t%d\t%4.2f\t%d\n' % (tempInterior, tempExterior,CO2, humedadInterior, velocidadViento, luxExterior, not lluvia))
        f.close

    sleep(5 * 60)

