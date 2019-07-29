# ██╗      █████╗  ██╗████████╗██╗   ██╗
# ██║     ██╔══██╗███║╚══██╔══╝██║   ██║
# ██║     ███████║╚██║   ██║   ██║   ██║
# ██║     ██╔══██║ ██║   ██║   ╚██╗ ██╔╝
# ███████╗██║  ██║ ██║   ██║    ╚████╔╝
# ╚══════╝╚═╝  ╚═╝ ╚═╝   ╚═╝     ╚═══╝

import time
import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("$SYS/#")

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 32775, 60)

try:
    client.loop_forever()
except KeyboardInterrupt:
    client.disconnect()
    print("Exiting main thread")
    time.sleep(2) 
