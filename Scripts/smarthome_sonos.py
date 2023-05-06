# Este script se utiliza como estudio del acceso al altavoz Sonos y de la generación de mensajes, que se
# añadirá al script de gestión de actuadores.

from soco import SoCo
import soco
from gtts import gTTS

# IP del Sonos 192.168.7.12
sonos = SoCo('192.168.7.12')
sonos.status_light = True
sonos.volume = 30

tts = gTTS('Prueba de audio', lang='es')
tts.save('prueba.mp3')

sonos.play_uri("172.17.0.:8080/prueba.mp3")