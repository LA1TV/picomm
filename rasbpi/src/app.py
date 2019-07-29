# ██╗      █████╗  ██╗████████╗██╗   ██╗
# ██║     ██╔══██╗███║╚══██╔══╝██║   ██║
# ██║     ███████║╚██║   ██║   ██║   ██║
# ██║     ██╔══██║ ██║   ██║   ╚██╗ ██╔╝
# ███████╗██║  ██║ ██║   ██║    ╚████╔╝
# ╚══════╝╚═╝  ╚═╝ ╚═╝   ╚═╝     ╚═══╝

import time
import paho.mqtt.client as mqtt
import logging
import gi
import sys
import json

from core.audio_source import AudioSource
from core.audio_mixer import AudioMixer

gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst, GLib

Gst.init(None)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

sources = dict()
mixer = AudioMixer("mixer")

def on_connect(client, userdata, flags, rc):
    logging.info("Connected with result code "+str(rc))
    client.subscribe("comms/connect")

def on_message(client, userdata, msg):
    logger.debug('on_message payload: %s', str(msg.payload))
    source_index = len(sources) + 1
    source_name = "source_%s" % source_index
    payload = json.loads(str(msg.payload))

    source = AudioSource(source_name, payload["host"], payload["port"])
    audiomixer.link(source)
    sources[source_name] = source

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect("localhost", 1883, 60)
except ConnectionRefusedError:
    logging.error("failed to connect to mqtt broker")
    sys.exit(1)

try:
    loop = GLib.MainLoop()
    logging.info("Waiting for messages")
    client.loop_start()
    loop.run()
except KeyboardInterrupt:
    for _, source in sources.items():
        source.stop()
        source = None

    loop.quit()
    client.loop_stop()
    client.disconnect()
    logging.info("Exiting main thread")
    sys.exit(0)
