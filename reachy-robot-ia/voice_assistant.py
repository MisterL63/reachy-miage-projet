import os
import time
import cv2
import sounddevice as sd
from scipy.io.wavfile import write
import httpx
from gtts import gTTS
import pygame
from reachy_mini import ReachyMini
import numpy as np

# --- CONFIGURATION MATÉRIEL REACHY ---
API_BASE_URL = "http://127.0.0.1:8080"
AUDIO_RECORD_FILE = "temp_user_input.wav"
AUDIO_WAKE_FILE = "temp_wake_input.wav"
AUDIO_RESPONSE_FILE = "temp_robot_response.mp3"

SAMPLERATE = 16000
RECORD_DURATION = 5        # Durée d'écoute de la question (secondes)
WAKE_RECORD_DURATION = 3   # Durée d'écoute par tranche pour le Mot-Clé (secondes)

# 🛠️ PERIPHERIQUES ROBOT
ROBOT_HOST = "reachy.local" 
ROBOT_MIC_ID = 5           # ID du microphone Reachy Mini Audio
CAMERA_INDEX = 0          # Index de la caméra Reachy
ROBOT_SPEAKER_NAME = "Interphone avec annulation d'écho (Reachy Mini Audio)" # Nom du haut-parleur Reachy

# Phonétiques tolérées par Whisper pour le mot-clé "Reachy"
WAKE_WORDS = ["reachy", "richy", "richi", "ritchie", "reachi", "rishi", "ritschi", "ricchi"]


# ==========================================
# 🔊 SYNTHÈSE VOCALE (TTS)
# ==========================================
def speak(text: str, lang: str = "fr"):
    """Transforme le texte en parole et le lit sur les haut-parleurs du robot."""
    print(f"\n🤖 Reachy dit : « {text} »")

    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save(AUDIO_RESPONSE_FILE)

    # Initialise Pygame sur le haut-parleur de Reachy
    try:
        pygame.mixer.init(devicename=ROBOT_SPEAKER_NAME)
    except Exception:
        pygame.mixer.init()

    pygame.mixer.music.load(AUDIO_RESPONSE_FILE)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

    pygame.mixer.music.unload()
    pygame.mixer.quit()
    time.sleep(0.3)

    if os.path.exists(AUDIO_RESPONSE_FILE):
        try:
            os.remove(AUDIO_RESPONSE_FILE)
        except Exception:
            pass


# ==========================================
# 🎙️ DÉTECTION MOT-CLÉ (WAKE WORD)
# ==========================================
def listen_for_wakeword() -> bool:
    """Écoute en continu par tranches courtes pour détecter 'Hey Reachy'."""
    # Capture forcée sur le micro Reachy (device=ROBOT_MIC_ID)
    audio_data = sd.rec(
        int(WAKE_RECORD_DURATION * SAMPLERATE), 
        samplerate=SAMPLERATE, 
        channels=1, 
        dtype='int16', 
        device=ROBOT_MIC_ID
    )
    sd.wait()
    write(AUDIO_WAKE_FILE, SAMPLERATE, audio_data)

    url = f"{API_BASE_URL}/api/v1/stt"
    try:
        with open(AUDIO_WAKE_FILE, "rb") as f:
            files = {"file": (AUDIO_WAKE_FILE, f, "audio/wav")}
            response = httpx.post(url, files=files, timeout=10.0)
            
        if response.status_code == 200:
            text = (response.json().get("transcription") or "").strip().lower()
            if text:
                for kw in WAKE_WORDS:
                    if kw in text:
                        print(f"\n🎯 MOT-CLÉ DÉTECTÉ ! (« {text} »)")
                        return True
    except Exception:
        pass
    finally:
        if os.path.exists(AUDIO_WAKE_FILE):
            try:
                os.remove(AUDIO_WAKE_FILE)
            except Exception:
                pass
    return False


# ==========================================
# 🎙️ CAPTURE & TRANSCRIPTION DE QUESTION
# ==========================================
def record_audio(duration: int = RECORD_DURATION) -> str:
    """Enregistre la question de l'utilisateur."""
    time.sleep(0.3)
    print(f"\n🎙️ Posez votre question ({duration} secondes)... PARLEZ MAINTENANT !")
    
    # Capture forcée sur le micro Reachy (device=ROBOT_MIC_ID)
    audio_data = sd.rec(
        int(duration * SAMPLERATE), 
        samplerate=SAMPLERATE, 
        channels=1, 
        dtype='int16', 
        device=ROBOT_MIC_ID
    )
    sd.wait()
    
    write(AUDIO_RECORD_FILE, SAMPLERATE, audio_data)
    print("✅ Enregistrement terminé.")
    return AUDIO_RECORD_FILE


def transcribe_audio(file_path: str) -> str:
    """Envoie l'audio à l'API Whisper."""
    print("⚡ Transcription audio en cours (Whisper)...")
    url = f"{API_BASE_URL}/api/v1/stt"
    
    with open(file_path, "rb") as f:
        files = {"file": (file_path, f, "audio/wav")}
        response = httpx.post(url, files=files, timeout=30.0)
        
    if response.status_code == 200:
        data = response.json()
        transcription = (data.get("transcription") or data.get("text") or "").strip()
        print(f"📝 Vous avez dit : « {transcription} »")
        return transcription
    else:
        print(f"❌ Erreur STT ({response.status_code}): {response.text}")
        return ""


# ==========================================
# 🎥 VISION / SCAN DE CARTE ÉTUDIANTE
# ==========================================
def scan_student_card() -> str:
    """Conserve Reachy en position haute et libère la caméra USB pour OpenCV."""
    print("\n🎥 Préparation du scan carte...")

    # 1. Libération de la caméra tout en gardant les moteurs alimentés
    try:
        mini = ReachyMini()
        mini.release_media()
        time.sleep(0.5)
    except Exception as e:
        print(f"⚠️ Avertissement connexion robot : {e}")

    # 2. Capture du QR Code via OpenCV
    cap = cv2.VideoCapture(0)
    qr_detector = cv2.QRCodeDetector()

    if not cap.isOpened():
        print("❌ Impossible d'accéder à la caméra.")
        return ""

    card_id = ""
    start_time = time.time()

    while time.time() - start_time < 15:
        ret, frame = cap.read()
        if not ret:
            break

        data, bbox, _ = qr_detector.detectAndDecode(frame)
        if data:
            card_id = data.strip()
            print(f"✅ CARTE SCANNÉE : {card_id}")

            if bbox is not None:
                n = len(bbox[0])
                for i in range(n):
                    pt1 = tuple(map(int, bbox[0][i]))
                    pt2 = tuple(map(int, bbox[0][(i + 1) % n]))
                    cv2.line(frame, pt1, pt2, (0, 255, 0), 3)

            cv2.imshow("Scan Carte Etudiante", frame)
            cv2.waitKey(1000)
            break

        cv2.imshow("Scan Carte Etudiante", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return card_id

# ==========================================
# 🧠 TRAITEMENT NLP & MCP MIDDLEWARE
# ==========================================
def process_intent(user_text: str, params: dict = None) -> dict:
    """Consulte le Cœur IA FastAPI et le Middleware."""
    url = f"{API_BASE_URL}/api/v1/process"
    payload = {"text": user_text, "params": params or {}}
    
    response = httpx.post(url, json=payload, timeout=30.0)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Erreur Process ({response.status_code}): {response.text}")
        return {}


def format_robot_reply(mcp_res: dict) -> str:
    """Mise en forme fluide de la réponse vocale du robot."""
    if not mcp_res:
        return "Désolé, une erreur s'est produite."

    if mcp_res.get("action_requise") == "REQUIRE_SCAN":
        return mcp_res.get("message", "Veuillez scanner votre carte étudiante.")

    if "donnees" in mcp_res:
        donnees = mcp_res["donnees"]
        prenom = donnees.get("prenom", "étudiant")
        nom = donnees.get("nom", "")
        formation = donnees.get("formation", "")
        notes = donnees.get("notes", {})
        
        reply = f"Authentification réussie. Bonjour {prenom} {nom}, inscrit en {formation}."
        if notes:
            notes_str = ", ".join([f"{matiere} : {note}/20" for matiere, note in notes.items()])
            reply += f" Voici vos notes : {notes_str}."
        return reply

    return (
        mcp_res.get("message") 
        or mcp_res.get("response") 
        or mcp_res.get("erreur") 
        or "Demande traitée."
    )


# ==========================================
# 🔄 BOUCLE PRINCIPALE EN CONTINU
# ==========================================
def run_voice_assistant():
    print("==================================================")
    print("🤖 ASSISTANT VOCAL & VISION REACHY - AUTONOME")
    print("==================================================")
    print("💡 Dites « Hey Reachy ! » pour réveiller le robot.")
    print("💡 Appuyez sur Ctrl+C dans le terminal pour tout stopper.\n")
    
    speak("Bonjour ! Je suis Reachy. Dites 'Hey Reachy' pour me parler.")
    
    try:
        while True:
            print("\r👀 En attente du mot-clé « Hey Reachy ! »...", end="", flush=True)
            
            # 1. Attente du Mot-Clé
            if listen_for_wakeword():
                speak("Oui ? Je vous écoute !")
                
                # 2. Capture de la question
                audio_file = record_audio()
                
                # 3. Transcription STT
                user_text = transcribe_audio(audio_file)
                if not user_text:
                    speak("Je n'ai pas entendu votre question.")
                    continue

                # 4. Traitement IA & MCP
                print("🧠 Analyse de la demande...")
                result = process_intent(user_text)
                mcp_res = result.get("mcp_response", {})

                # 5. Gestion Carte / Réponse
                if mcp_res.get("action_requise") == "REQUIRE_SCAN":
                    prompt_msg = format_robot_reply(mcp_res)
                    speak(prompt_msg)
                    
                    card_id = scan_student_card()
                    
                    if card_id:
                        speak("Carte détectée, consultation de votre dossier en cours.")
                        second_result = process_intent(user_text, params={"id_carte": card_id})
                        final_reply = format_robot_reply(second_result.get("mcp_response", {}))
                        speak(final_reply)
                    else:
                        speak("Aucune carte n'a été détectée. Opération annulée.")
                else:
                    final_reply = format_robot_reply(mcp_res)
                    speak(final_reply)
                
                print("\n🔄 Reachy retourne en veille...\n")
                time.sleep(1.0)

    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt de l'assistant vocal Reachy.")
        speak("Au revoir !")
    finally:
        if os.path.exists(AUDIO_RECORD_FILE):
            try:
                os.remove(AUDIO_RECORD_FILE)
            except Exception:
                pass


if __name__ == "__main__":
    run_voice_assistant()