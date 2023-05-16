# Este script se utiliza como estudio del acceso al altavoz Sonos y de la generación de mensajes, que se
# añadirá al script de gestión de actuadores.

from soco import SoCo
from gtts import gTTS
from ftplib import FTP

# Establecemos una conexión con el servidor de audios
ftp = FTP('192.168.66.38', 'ubuntu', 'ubuntu')
ftp.cwd('/home/ubuntu/audios')

# Generamos el audio a reproducir
tts = gTTS('Prueba de audio', lang='es')
tts.save('prueba.mp3')

# Subimos el archivo al servidor, finalmente cerramos la conexión y el archivo
with open('prueba.mp3', 'rb') as audio:
    ftp.storbinary('STOR prueba.mp3', audio)
ftp.quit()

# Ahora creamos una instancia del altavoz Sonos y pedimos que reproduzca el audio
sonos = SoCo('192.168.7.14')
sonos.status_light = False
sonos.volume = 5
sonos.play_uri("https://vgmsite.com/soundtracks/legend-of-zelda-the-30th-anniversary-game-music/rsmuorbhbm/1-01%20Title%20-%20Legend%20of%20Zelda.mp3")