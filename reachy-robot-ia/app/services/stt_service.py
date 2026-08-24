import io
from faster_whisper import WhisperModel

class STTService:
    def __init__(self, model_size: str = "small"):
        print(f"[STT] Chargement du modèle Whisper ({model_size})...")
        # Sur CPU avec int8 pour garder une exécution très rapide
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")

    def transcribe(self, audio_bytes: bytes) -> str:
        audio_stream = io.BytesIO(audio_bytes)
        segments, _ = self.model.transcribe(audio_stream, language="fr")
        return " ".join([s.text for s in segments]).strip()