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

gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst, GLib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def on_connect(client, userdata, flags, rc):
    logging.info("Connected with result code "+str(rc))
    client.subscribe("comms/new-client")

def on_message(client, userdata, msg):
    logger.debug('on_message payload: %s', str(msg.payload))

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
    loop.quit()
    client.loop_stop()
    client.disconnect()
    logging.info("Exiting main thread")
    time.sleep(2)
    sys.exit(0)
