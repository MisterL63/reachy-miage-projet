import sounddevice as sd
from scipy.io.wavfile import read

try:
    # Lecture du fichier généré à l'étape précédente
    samplerate, audio_data = read('test_enregistrement.wav')
    print("🔊 Lecture du son dans ton casque...")
    sd.play(audio_data, samplerate)
    sd.wait()  # Attend la fin de la lecture
    print("✅ Lecture terminée !")
except FileNotFoundError:
    print("❌ Erreur : Exécute d'abord 'test_micro.py' pour créer le fichier audio.")