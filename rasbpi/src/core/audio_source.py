import logger

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

class AudioSource:
    def __init__(self, name, host, port):
        self.log = logging.getLogger('AudioSource[{}]'.format(name))

        assert host or port
        self.pipeline = None
        self.name = name
        self.host = host
        self.port = port
        self.audio_caps = "application/x-rtp,channels=(int)2,format=(string)S16LE,media=(string)audio,payload=(int)96,clock-rate=(int)44100,encoding-name=(string)L24"
        self.launch_pipeline()

    def __str__(self):
        return 'AudioSource[{name}] host={host}, port={port}'.format(
            name=self.name,
            host=self.host,
            port=self.port
        )

    def build_pipeline():
        

    def launch_pipeline():
        pipeline = """
            udpsrc uri=udp://{host}:{port} caps='{caps}' !
            rtpL24depay !
            audioconvert !
            queue name=aout
        """.format(
            host=self.host,
            port=self.port,
            caps=self.audio_caps,
        )

        self.build_pipeline(pipeline)
    

    