import time
import cv2
from reachy_mini import ReachyMini

print("🤖 Connexion au Reachy Mini...")
mini = ReachyMini()

print("🔓 Demande de libération de la caméra au Daemon...")
mini.release_media()
time.sleep(1.0)  # Temps de libération du périphérique USB par Windows

print("🎥 Test d'accès vidéo avec OpenCV...")
cap = cv2.VideoCapture(CAMERA_INDEX)

if cap.isOpened():
    ret, frame = cap.read()
    if ret:
        print("✅ SUCCÈS : Le robot est DEBOUT et la caméra est ACCESSIBLE !")
        cv2.imshow("Test Reachy Upright", frame)
        cv2.waitKey(2000)
        cv2.destroyAllWindows()
    else:
        print("⚠️ Caméra ouverte mais flux vide.")
    cap.release()
else:
    print("❌ La caméra reste bloquée.")