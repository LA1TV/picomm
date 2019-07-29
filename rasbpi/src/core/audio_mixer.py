import logging
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

class AudioMixer():
    def __init__(self, name):
        self.log = logging.getLogger('AudioMixer[{}]'.format(name))
        self.name = name
        self.pipeline = None
        self.linked_elements = {}
        self.audio_caps = "audio/x-raw,format=S16LE,channels=2,layout=interleaved,rate=44100"
        self.launch_pipeline()

    def __str__(self):
        return 'AudioMixer[{name}]'.format(
            name=self.name
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
        self.log.debug('Creating Mixing-Pipeline:\n%s', pipeline)
        self.pipeline = Gst.parse_launch(pipeline)
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message::state-changed", self._on_state_change)
        bus.connect("message::eos", self._on_eos)
        bus.connect("message::error", self._on_error)
        self.pipeline.set_state(Gst.State.PLAYING)

    def launch_pipeline(self):
        pipeline = """
            audiotestsrc is-live=true volume=0 !
            audiorate !
            audioconvert !
            audioresample !
            {caps} !
            audiomixer name=mixer !
            queue !
            autoaudiosink sync=false
        """.format(
            caps=self.audio_caps,
            output=self.name,
            )
        self.build_pipeline(pipeline)

    def build_link_elements(self, source):
        intersrc = Gst.ElementFactory.make('interaudiosrc')
        intersrc.set_property('channel', source.get_audio_channel())
        self.log.info("creating interaudiosrc channel=%s", source.get_audio_channel())

        queue = Gst.ElementFactory.make('queue')

        return intersrc, queue

    #region Source Linking methods
    def link(self, source):
        if source in self.linked_elements:
            self.log.warning('%s already linked to mixer', source.name)
            return False

        intersrc, queue = self.build_link_elements(source)
        self.pipeline.add(intersrc)
        self.pipeline.add(queue)

        mixer = self.pipeline.get_by_name('mixer')

        queue_src_pad = queue.get_static_pad('src')
        template = mixer.get_pad_template('sink_%u')
        mixer_sink_pad = mixer.request_pad(template)

        if not intersrc.link(queue):
            self.log.error('failed linking intervideosrc and queue')
            return False

        intersrc.sync_state_with_parent()
        queue.sync_state_with_parent()

        if (queue_src_pad.link(mixer_sink_pad)) != Gst.PadLinkReturn.OK:
            self.log.error('failed to link queue and video mixer')
            return False

        self.linked_elements[source] = {}
        self.linked_elements[source]['intersrc'] = intersrc
        self.linked_elements[source]['queue'] = queue
        return True

    def unlink(self, source):
        if source not in self.linked_elements:
            self.log.warning('mixer is not linked to %s', source.name)
            return False

        intersrc = self.linked_elements[source]['intersrc']
        queue = self.linked_elements[source]['queue']
        mixer = self.pipeline.get_by_name('mixer')

        assert intersrc, queue

        mixer_src_pad = queue.get_static_pad('src')
        mixer_pad = mixer_src_pad.get_peer()

        if not mixer_src_pad.unlink(mixer_pad):
            self.log.error('failed to unlink queue and mixer')
            return False

        mixer.release_request_pad(mixer_pad)

        intersrc.set_state(Gst.State.NULL)
        queue.set_state(Gst.State.NULL)

        self.pipeline.remove(intersrc)
        self.pipeline.remove(queue)

        del self.linked_elements[source]
        return True

    #endregion