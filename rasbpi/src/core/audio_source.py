import logging
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

    def _on_state_change(self, _, message):
        if message.src == self.pipeline:
            old_state, new_state, pending = message.parse_state_changed()
            self.log.debug("StateChanged: old_state=%s, new_state=%s, pending=%s",
                           old_state.value_nick.upper(),
                           new_state.value_nick.upper(),
                           pending.value_nick.upper())

    def _on_eos(self, _, __):
        self.log.warning("End of Stream")

    def _on_error(self, _, message):
        (error, debug) = message.parse_error()
        self.log.error('#%u: %s', error.code, debug)

    def build_pipeline(self, pipeline):
        self.log.debug('Launching Source-Pipeline:\n%s', pipeline)
        self.pipeline = Gst.parse_launch(pipeline)
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message::state-changed", self._on_state_change)
        bus.connect("message::eos", self._on_eos)
        bus.connect("message::error", self._on_error)
        self.pipeline.set_state(Gst.State.PLAYING)

    def stop():
        self.log.debug('Stopping pipeline')
        self.pipeline.set_state(Gst.State.NULL)

    def launch_pipeline(self):
        pipeline = """
            udpsrc uri=udp://{host}:{port} caps="{caps}" !
            rtpL24depay !
            audioconvert !
            queue !
            tee name=atee
            atee. ! queue ! interaudiosink channel={channel}
        """.format(
            host=self.host,
            port=self.port,
            caps=self.audio_caps,
            channel=self.name
        )

        self.build_pipeline(pipeline)
    

    