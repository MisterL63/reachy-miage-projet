import cv2
import sounddevice as sd


def get_reachy_speaker():
    """Trouve le haut-parleur Reachy ou utilise le périphérique par défaut."""
    devices = sd.query_devices()
    for dev in devices:
        if dev["max_output_channels"] > 0 and "reachy" in dev["name"].lower():
            print(f"🔊 Haut-parleur Reachy détecté : {dev['name']}")
            return dev["name"]
    print("🔊 Aucun haut-parleur Reachy trouvé. Utilisation du haut-parleur par défaut.")
    return None


def get_reachy_microphone():
    """Trouve l'ID du microphone Reachy ou l'ID par défaut."""
    devices = sd.query_devices()
    for index, dev in enumerate(devices):
        if dev["max_input_channels"] > 0 and "reachy" in dev["name"].lower():
            print(f"🎙️ Microphone Reachy détecté (Index {index}) : {dev['name']}")
            return index

    default_mic = sd.default.device[0]
    print(f"🎙️ Aucun micro Reachy trouvé. Utilisation du micro par défaut (Index {default_mic}).")
    return default_mic if default_mic is not None else 0


def get_reachy_camera_index():
    """Trouve l'index de la caméra vidéo exploitable (hors DroidCam/virtuelles)."""
    for index in range(5):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret:
                print(f"🎥 Caméra valide détectée sur l'index : {index}")
                return index
    print("⚠️ Aucune caméra fonctionnelle détectée. Utilisation de l'index 0.")
    return 0