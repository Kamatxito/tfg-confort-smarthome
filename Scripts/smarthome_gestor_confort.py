# En este script se gestiona qué parámetros son controlados automáticamente. Primero pregunta al usuario por
# qué campos controlar y entonces actúa sobre la smarthome en función de los valores que se van obteniendo.

import requests
from time import sleep

# Balizas para activar cada control
baliza_temp = False

# Configuración para el acceso a los sensores
dir = "http://remote:LabSmarthome21@192.168.7.210/scada-remote" # Direccion de la API
parametros_GET = { # Parametros para la conexion a la API
    'm': 'json', # Formato de salida
    'r': 'grp', # Request
    'fn': 'getvalue', # Función a ejecutar
    'alias': '0/0/0' # Dirección del objeto
}
parametros_POST = { # Parametros para la conexion a la API
    'm': 'json', # Formato de salida
    'r': 'grp', # Request
    'fn': 'write', # Función a ejecutar
    'alias': '0/0/0', # Dirección del objeto
    'value': '' # Nuevo valor del objeto
}
def GET_datos(parametros):
    r = requests.get(url=dir, params=parametros)
    return r.json()
def POST_datos(parametros):
    r = requests.post(url=dir, params=parametros)
    print(r.status_code)
    print(r.json())

# Consultas al usuario
opcion = input("Activar control de temperatura (True/False): ")
baliza_temp = bool(opcion)

while (True):
    # Gestor de confort
    if (baliza_temp):
        # Recogida de datos
        parametros_GET['alias'] = '3/2/5'
        temp_exterior = GET_datos(parametros_GET)
        temp_exterior += 0.0 # Para evitar valores enteros
        parametros_GET['alias'] = '3/1/1'
        temp_interior = GET_datos(parametros_GET)
        temp_interior += 0.0 # Para evitar valores enteros
        parametros_GET['alias'] = '2/3/7'
        altura_ventana = GET_datos(parametros_GET)

        # Gestión de cada caso
        if ((temp_interior < 20) and (temp_exterior > temp_interior) and (altura_ventana==100)):
            print("Temperatura baja en el interior, abriendo ventanas.")
            parametros_POST['alias'] = '2/3/5'
            parametros_POST['value'] = 0
            POST_datos(parametros_POST)
        if ((temp_interior > 25) and (temp_exterior > temp_interior) and (altura_ventana<100)):
            print("Temperatura alta en el interior, cerrando ventanas.")
            parametros_POST['alias'] = '2/3/5'
            parametros_POST['value'] = 1
            POST_datos(parametros_POST)
    sleep(5*60)