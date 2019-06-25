import logging
try:
    import sounddevice as sd
except:
    sd = None

from senseye_utils.date_utils import timestamp_now
from . input import Input

log = logging.getLogger(__name__)


class AudioPortInput(Input):
    '''
    Reads in audio using portaudio/sounddevice.
    Args:
        id (str): device index
        config (dict): Configuration dictionary. Accepted keywords:
            channels (int): number of audio channels
            block_size (int): number of bytes to read in per iteration
            samplerate (int): audio sample rate
    '''

    def __init__(self, id=0, config={}):

        defaults = {
            'channels': 1,
            'blocksize': 1024,
            'samplerate': 44100,
        }
        Input.__init__(self, id=id, config=config, defaults=defaults)

    def configure(self):
        '''
        Supported configurations: samplerate, channels, blocksize
        '''
        device_info = sd.query_devices(self.id, 'input')
        if 'samplerate' not in self.config:
            self.config['samplerate'] = int(device_info['default_samplerate'])
        if 'channels' not in self.config:
            self.config['channels'] = device_info['max_input_channels']

    def open(self):
        '''Opens Audio stream'''
        try:
            self.configure()
            self.input = sd.InputStream(
                device=self.id,
                channels=self.config['channels'],
                samplerate=self.config['samplerate']
            )
            self.input.start()
        except Exception as e:
            log.warning(f'Failed to load audio stream: {e}')
        self.log_start()

    def read(self):
        '''Reads in audio blocks'''
        audio = None

        if self.input:
            audio, overflow = self.input.read(self.config['blocksize'])
            if overflow:
                audio = None
                log.warning('Audio block overflow')

        return audio, timestamp_now()

    def close(self):
        if self.input:
            self.input.close()
        self.input = None

# Fallback for no pylon
if sd is None:
    class AudioPortInput(Input):
        def __init__(self, *args, **kargs):
            Input.__init__(self)
            log.error("SoundDevice not found")
