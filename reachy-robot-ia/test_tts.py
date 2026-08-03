import os
import time
from gtts import gTTS
import pygame

def speak(text: str, lang: str = "fr"):
    filename = "temp_response.mp3"
    print(f"🔊 Génération de la voix pour : \"{text}\"")

    # 1. Génération de l'audio MP3
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save(filename)

    # 2. Lecture du fichier audio
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    # 3. Attente de la fin de la lecture
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

    # 4. Nettoyage
    pygame.mixer.quit()
    if os.path.exists(filename):
        os.remove(filename)

    print("✅ Lecture terminée !")

if __name__ == "__main__":
    test_phrase = "Bonjour ! Je suis le robot Reachy. Le professeur Tounsi est actuellement en salle C3."
    speak(test_phrase)