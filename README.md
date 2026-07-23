# reachy-miage-projet
Notre projet consiste à donner vie à un robot d'accueil interactif, le Reachy Mini, pour orienter et renseigner les étudiants de la MIAGE.

## Démarrage Rapide & Tests du Backend

### 1. Démarrer le Middleware (Express / Node.js)
Ouvrez un premier terminal dans le dossier du middleware :

```bash
cd reachy-middleware-api
npm install          # À exécuter uniquement lors du tout premier lancement
node server.js
```

Le serveur Express est accessible sur http://localhost:3000.

### 2. Démarrer le Cœur IA (FastAPI / Python)
Ouvrez un second terminal dans le dossier du serveur IA :

```bash

cd reachy-robot-ia

# Activation de l'environnement virtuel (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Lancement du serveur FastAPI
uvicorn app.main:app --reload --port 8000
```

Le serveur FastAPI est accessible sur http://127.0.0.1:8000.

### 3. Tester la Chaîne Complète (Swagger UI)
Rendez-vous sur la documentation interactive : http://127.0.0.1:8000/docs.

Dépliez la route POST /api/v1/process et cliquez sur Try it out.

Saisissez le corps de requête JSON suivant :

```bash
    {
    "text": "Où est le professeur Tounsi ?",
    "params": {
        "nom_prof": "Tounsi"
    }
    }
```

Cliquez sur Execute.