import os
import time
import sounddevice as sd
from scipy.io.wavfile import write
import httpx
from gtts import gTTS
import pygame

# --- CONFIGURATION ---
API_BASE_URL = "http://127.0.0.1:8000"
AUDIO_RECORD_FILE = "temp_user_input.wav"
AUDIO_RESPONSE_FILE = "temp_robot_response.mp3"
SAMPLERATE = 16000
RECORD_DURATION = 5  # Durée d'écoute en secondes


def speak(text: str, lang: str = "fr"):
    """Synthèse vocale (TTS) : transforme le texte en audio et le lit."""
    print(f"\n🤖 Reachy dit : « {text} »")
    
    # Génération du fichier audio
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save(AUDIO_RESPONSE_FILE)

    # Lecture via Pygame
    pygame.mixer.init()
    pygame.mixer.music.load(AUDIO_RESPONSE_FILE)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

    pygame.mixer.music.unload()
    pygame.mixer.quit()
    time.sleep(0.5)  # Libération du canal audio
    
    if os.path.exists(AUDIO_RESPONSE_FILE):
        try:
            os.remove(AUDIO_RESPONSE_FILE)
        except Exception:
            pass


def record_audio(duration: int = RECORD_DURATION) -> str:
    """Enregistre le son du microphone par défaut."""
    time.sleep(0.5)  # Pause pour libérer la carte son
    print(f"\n🎙️ Écoute pendant {duration} secondes... PARLEZ MAINTENANT !")
    
    audio_data = sd.rec(int(duration * SAMPLERATE), samplerate=SAMPLERATE, channels=1, dtype='int16')
    sd.wait()
    
    write(AUDIO_RECORD_FILE, SAMPLERATE, audio_data)
    print("✅ Enregistrement terminé.")
    return AUDIO_RECORD_FILE


def transcribe_audio(file_path: str) -> str:
    """Envoie l'audio à Whisper (FastAPI)."""
    print("⚡ Transcription audio en cours (Whisper)...")
    url = f"{API_BASE_URL}/api/v1/stt"
    
    with open(file_path, "rb") as f:
        files = {"file": (file_path, f, "audio/wav")}
        response = httpx.post(url, files=files, timeout=30.0)
        
    if response.status_code == 200:
        data = response.json()
        # Fix : On récupère la clé "transcription" renvoyée par app/main.py
        transcription = (data.get("transcription") or data.get("text") or "").strip()
        print(f"📝 Vous avez dit : « {transcription} »")
        return transcription
    else:
        print(f"❌ Erreur STT ({response.status_code}): {response.text}")
        return ""


def process_intent(user_text: str) -> str:
    """Envoie la transcription à l'IA et au Middleware."""
    print("🧠 Analyse de l'intention et consultation du Middleware...")
    url = f"{API_BASE_URL}/api/v1/process"
    
    payload = {"text": user_text}
    response = httpx.post(url, json=payload, timeout=30.0)
    
    if response.status_code == 200:
        data = response.json()
        mcp_res = data.get("mcp_response", {})
        
        # Gestion unifiée des réponses (MCP message, discussion CHAT ou erreur)
        msg = (
            mcp_res.get("message") 
            or mcp_res.get("response") 
            or mcp_res.get("erreur")
        )
        if msg:
            return msg
        
        return f"Intention détectée : {data.get('analysis', {}).get('intent')}"
    else:
        print(f"❌ Erreur Process ({response.status_code}): {response.text}")
        return "Désolé, je n'ai pas pu traiter votre demande."


def run_voice_assistant():
    print("==================================================")
    print("🤖 ASSISTANT VOCAL REACHY - PRÊT")
    print("==================================================")
    
    speak("Bonjour ! Je suis à votre écoute.")
    
    try:
        # 1. Capture Audio
        audio_file = record_audio()
        
        # 2. Transcription (STT)
        user_text = transcribe_audio(audio_file)
        
        if not user_text:
            speak("Je n'ai pas entendu votre question.")
            return

        # 3. Traitement IA & MCP Middleware
        robot_response = process_intent(user_text)
        
        # 4. Réponse Vocale (TTS)
        speak(robot_response)
        
    except Exception as e:
        print(f"\n❌ Une erreur est survenue : {e}")
        speak("Une erreur s'est produite lors du traitement.")
    finally:
        if os.path.exists(AUDIO_RECORD_FILE):
            try:
                os.remove(AUDIO_RECORD_FILE)
            except Exception:
                pass


if __name__ == "__main__":
    run_voice_assistant()