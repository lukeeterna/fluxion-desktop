# VAD Wrapper - usa webrtcvad se silero non disponibile
try:
    from src.vad import FluxionVAD, VADConfig, VADState
except ImportError:
    print('[WARN] Silero VAD non disponibile, uso webrtcvad')
    import webrtcvad
    
    class VADState:
        IDLE = 'IDLE'
        LISTENING = 'LISTENING'
        SPEECH_DETECTED = 'SPEECH_DETECTED'
    
    class VADConfig:
        def __init__(self, **kwargs):
            self.sample_rate = 16000
            self.frame_duration = 30
            self.threshold = 0.5
    
    class FluxionVAD:
        def __init__(self, config=None):
            self.config = config or VADConfig()
            self.vad = webrtcvad.Vad(2)  # Mode 2 = aggressive
            self.state = VADState.IDLE
        
        def process(self, audio_bytes):
            try:
                is_speech = self.vad.is_speech(audio_bytes, self.config.sample_rate)
                return VADState.SPEECH_DETECTED if is_speech else VADState.IDLE
            except:
                return VADState.IDLE
        
        def reset(self):
            self.state = VADState.IDLE
