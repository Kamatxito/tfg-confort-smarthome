# SCRIPT DE HABLAR CON EL SONOS
# IMPORTAR MODULOS
from soco import SoCo
import soco
from gtts import gTTS

# IP del Sonos 192.168.7.12
sonos = SoCo('192.168.7.12')
sonos.status_light = True
sonos.volume = 30

#tts = gTTS('El comfort térmico es adecuado', lang='es')
#tts.save('prueba.mp3')

sonos.play_uri("172.17.0.:8080/prueba.mp3")