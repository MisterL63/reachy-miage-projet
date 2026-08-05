# reachy-miage-projet
Notre projet consiste à donner vie à un robot d'accueil interactif, le Reachy Mini, pour orienter et renseigner les étudiants de la MIAGE.

# Reachy Robot - Backend & Cœur IA

Ce dépôt contient le backend du projet Reachy, composé de deux services principaux :
1. **Middleware API (Express / Node.js)** : Gestion des plannings et des données métiers.
2. **Cœur IA (FastAPI / Python)** : Traitement du langage naturel (NLP), Speech-to-Text (Whisper) et intégration MCP.

---

## Prérequis

- **Python 3.11.x** *(Obligatoire : PyTorch et faster-whisper ne sont pas encore pleinement compatibles avec Python 3.14+)*
- **Node.js** (v20+ LTS recommandé)
- **PowerShell** (sous Windows)

> ⚠️ **Note Sécurité PowerShell :** Si Windows bloque l'exécution des scripts (`npm` ou `Activate.ps1`), exécutez cette commande dans votre terminal :
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> ```

---

## 1. Installation & Configuration

### A. Middleware Express (Node.js)
Ouvrez un terminal et placez-vous dans le dossier du middleware :

```powershell
cd reachy-middleware-api

# Installation des paquets Node.js (express, cors...)
npm install

```
### B. Cœur IA FastAPI (Python 3.11)
Ouvrez un second terminal et placez-vous dans le dossier de l'IA :

```powershell
cd reachy-robot-ia

# 1. Création de l'environnement virtuel avec Python 3.11
py -3.11 -m venv .venv

# 2. Activation de l'environnement virtuel
.\.venv\Scripts\Activate.ps1

# 3. Installation des dépendances IA
pip install fastapi "uvicorn[standard]" pydantic faster-whisper transformers torch httpx mcp

```

## 2. Démarrage des Serveurs
### Terminal 1 : Middleware Express

```powershell
cd reachy-middleware-api
node server.js
```
Accessible sur http://localhost:3000

### Terminal 2 : Cœur IA FastAPI

```powershell
cd reachy-robot-ia
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8080
```

(Alternative si problème d'environnement global : .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8080)

Accessible sur http://127.0.0.1:8080

## 3. Validation & Test de la Chaîne Complète
Rendez-vous sur la documentation interactive : http://127.0.0.1:8080/docs.

Dépliez la route POST /api/v1/process et cliquez sur Try it out.

Injectez le JSON de test suivant :

```json
{
  "text": "Où est le professeur Tounsi ?",
  "params": {
    "nom_prof": "Tounsi"
  }
}
```

Cliquez sur Execute.

Résultat attendu (200 OK) :

```json{
  "analysis": {
    "intent": "SEARCH_PROF",
    "confidence": 0.92,
    "text": "Où est le professeur Tounsi ?"
  },
  "mcp_response": {
    "trouve": true,
    "message": "M. Tounsi donne actuellement un cours de Management en Salle C3."
  }
}
```
