import time
import numpy as np
from reachy_mini import ReachyMini

def go_to_neutral(mini):
    """Replace le robot dans sa position par défaut (tête droite, antennes baissées)."""
    mini.goto_target(antennas=np.deg2rad([0, 0]), duration=0.5)
    mini.look_at_world(x=0.4, y=0.0, z=0.1, duration=0.5)
    time.sleep(0.5)

def nod_yes(mini):
    """Mouvement pour dire 'Oui'."""
    print("👍 Animation : OUI")
    # Anciennement les antennes du 'Non'
    mini.goto_target(antennas=np.deg2rad([-20, 20]), duration=0.3)
    
    mini.look_at_world(x=0.4, y=0.0, z=-0.1, duration=0.3)
    time.sleep(0.3)
    mini.look_at_world(x=0.4, y=0.0, z=0.2, duration=0.4)
    time.sleep(0.4)
    
    go_to_neutral(mini)

def shake_no(mini):
    """Mouvement pour dire 'Non'."""
    print("👎 Animation : NON")
    # Anciennement les antennes du 'Oui'
    mini.goto_target(antennas=np.deg2rad([-45, 45]), duration=0.3)
    
    mini.look_at_world(x=0.4, y=0.2, z=0.1, duration=0.3)
    time.sleep(0.3)
    mini.look_at_world(x=0.4, y=-0.2, z=0.1, duration=0.4)
    time.sleep(0.4)
    
    go_to_neutral(mini)

def think(mini):
    """Mouvement 'Réflexion' avec effet de chargement."""
    print("🤔 Animation : RÉFLEXION (Chargement...)")
    
    # 1. Reachy baisse la tête (z=-0.1)
    mini.look_at_world(x=0.4, y=0.0, z=-0.1, duration=0.5)
    time.sleep(0.2) # Petite pause pour laisser la tête commencer à descendre
    
    # 2. Boucle d'animation des antennes (3 secondes = 3 itérations d'1 sec)
    for _ in range(3):
        # Antennes en haut
        mini.goto_target(antennas=np.deg2rad([-40, 40]), duration=0.5)
        time.sleep(0.5)
        # Antennes en bas
        mini.goto_target(antennas=np.deg2rad([0, 0]), duration=0.5)
        time.sleep(0.5)
    
    # 3. Fin de la réflexion, retour au neutre
    go_to_neutral(mini)

def sleep_pose(mini):
    """Position de repos (Sommeil). Tête baissée, antennes relâchées."""
    print("💤 Animation : SOMMEIL")
    mini.goto_target(antennas=np.deg2rad([0, 0]), duration=1.0)
    mini.look_at_world(x=0.4, y=0.0, z=-0.3, duration=1.0)
    # ⚠️ Pas de go_to_neutral() ici, car on veut qu'il RESTE endormi !

def wakeup(mini):
    """Position de réveil (Sursaut joyeux)."""
    print("✨ Animation : RÉVEIL")
    # Redresse la tête brusquement et lève les antennes (avec tes signes inversés)
    mini.goto_target(antennas=np.deg2rad([-45, 45]), duration=0.3)
    mini.look_at_world(x=0.4, y=0.0, z=0.2, duration=0.3)
    time.sleep(0.4)
    
    go_to_neutral(mini)

# Bloc de test
if __name__ == "__main__":
    print("🤖 Connexion au Reachy Mini (une seule fois pour tout le script)...")
    try:
        with ReachyMini() as robot:
            
            # Coupe le flux vidéo pour éviter l'erreur GStreamer
            if hasattr(robot, 'release_media'):
                robot.release_media()
                time.sleep(0.5)

            nod_yes(robot)
            time.sleep(0.5)
            
            shake_no(robot)
            time.sleep(0.5)
            
            think(robot)
            
    except Exception as e:
        print(f"❌ Erreur critique : {e}")

