import cv2

def scan_card():
    """Ouvre la caméra et attend la détection d'un QR code représentant la carte étudiante."""
    # 0 est la caméra par défaut (utilise 1 ou 2 si Reachy a plusieurs caméras)
    cap = cv2.VideoCapture(0)
    qr_detector = cv2.QRCodeDetector()

    if not cap.isOpened():
        print("❌ Impossible d'ouvrir la caméra.")
        return None

    print("🎥 Caméra activée ! Présentez votre carte étudiante (QR Code) devant la caméra.")
    print("👉 Appuyez sur 'q' pour quitter si besoin.")

    card_id = None

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Erreur de lecture de la caméra.")
            break

        # Détection et décodage du QR Code dans l'image
        data, bbox, _ = qr_detector.detectAndDecode(frame)

        if data:
            card_id = data
            print(f"\n✅ CARTE DÉTECTÉE ! Identifiant : {card_id}")
            
            # Dessine un rectangle vert autour du QR Code détecté
            if bbox is not None:
                n = len(bbox[0])
                for i in range(n):
                    pt1 = tuple(map(int, bbox[0][i]))
                    pt2 = tuple(map(int, bbox[0][(i + 1) % n]))
                    cv2.line(frame, pt1, pt2, (0, 255, 0), 3)

            cv2.imshow("Scan Carte Etudiante", frame)
            cv2.waitKey(1000)  # Affiche le résultat 1 seconde avant de fermer
            break

        # Affichage du flux vidéo
        cv2.imshow("Scan Carte Etudiante", frame)

        # Quitter avec la touche 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return card_id

if __name__ == "__main__":
    result = scan_card()
    if result:
        print(f"🎉 Code lu avec succès : {result}")
    else:
        print("⚠️ Aucun code n'a été scanné.")