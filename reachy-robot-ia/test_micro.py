import sounddevice as sd
from scipy.io.wavfile import write

# Configuration (16000 Hz est la fréquence idéale pour Whisper)
SAMPLERATE = 16000
DURATION = 5  # Durée de l'enregistrement en secondes

print("🎙️ Enregistrement démarré ! Parle dans ton micro pendant 5 secondes...")
audio_data = sd.rec(int(DURATION * SAMPLERATE), samplerate=SAMPLERATE, channels=1, dtype='int16')
sd.wait()  # Attend la fin des 5 secondes

# Sauvegarde dans un fichier test_enregistrement.wav
write('test_enregistrement.wav', SAMPLERATE, audio_data)
print("✅ Enregistrement terminé ! Fichier 'test_enregistrement.wav' sauvegardé.")