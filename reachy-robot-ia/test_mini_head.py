import time
from reachy_mini import ReachyMini

print("🤖 Connexion au Reachy Mini...")

try:
    with ReachyMini() as mini:
        print("📐 Redressement de la tête...")
        # Orientation vers le point (x=40cm devant, y=centré, z=10cm rehaussé)
        mini.look_at_world(x=0.4, y=0.0, z=0.1, duration=1.2)
        time.sleep(1.5)
        print("✅ Mouvement effectué avec succès !")

except Exception as e:
    print(f"❌ Erreur lors du mouvement : {e}")