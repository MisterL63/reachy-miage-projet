import re
import os
import json
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

# Charge les variables d'environnement depuis le fichier .env
load_dotenv()

class NLPService:
    def __init__(self):
        print("[NLP] Chargement du client LLM Hugging Face...")
        
        # Récupération du token Hugging Face depuis les variables d'environnement
        self.token = os.environ.get("HF_TOKEN")
        if not self.token:
            print("ATTENTION: La variable d'environnement HF_TOKEN n'est pas définie. L'API risque de refuser la connexion si le modèle nécessite une authentification.")
            
        # Utilisation d'un modèle performant via l'API Hugging Face (Modèle Chat compatible)
        self.model_id = "Qwen/Qwen2.5-72B-Instruct"
        self.client = InferenceClient(model=self.model_id, token=self.token)
        
        # Définition des outils/intentions pour le prompt du LLM
        self.intent_descriptions = {
            "SEARCH_PROF": "Trouver un professeur, chercher un contact enseignant, demander la salle d'un prof. L'IA DOIT extraire le nom du professeur de la phrase (sans les titres de civilité comme M., Mme) et le placer dans les paramètres sous la clé 'nom_prof'.",
            "GET_DOSSIER": "Accéder à son dossier étudiant, ses notes, son bulletin ou ses absences. L'IA peut extraire l'ID de la carte étudiante s'il est mentionné et le placer dans les paramètres sous la clé 'id_carte'.",
            "GET_ALL_PLANNINGS": "Demander l'emploi du temps, le planning complet ou l'agenda.",
            "GET_INFO_ADMIN": "Demander des informations administratives (inscription, secrétariat, règlement).",
            "CHAT": "L'utilisateur discute, dit bonjour, demande comment tu vas, ou pose une question courante sans rapport avec les autres intentions."
        }

    def classify(self, text: str) -> dict:
        intent = "UNKNOWN"
        confidence = 0.0
        params = {}
        chat_response = ""

        # L'IA analyse la phrase complète pour en comprendre le sens profond
        prompt = f"""Tu es Reachy, un robot assistant intelligent de l'université.
Ta tâche est d'analyser la requête de l'utilisateur pour comprendre son intention profonde et d'agir comme un routeur d'outils (MCP).
Tu dois répondre STRICTEMENT en JSON, sans aucun texte avant ou après.

Liste des outils / intentions disponibles :
{json.dumps(self.intent_descriptions, ensure_ascii=False, indent=2)}

RÈGLE D'OR :
- Analyse le sens de la phrase entière, ne te base pas juste sur des mots-clés.
- Si l'utilisateur demande quelque chose lié à une intention, extrais les paramètres nécessaires (comme 'nom_prof' pour SEARCH_PROF) et place-les dans "params".
- Si la requête de l'utilisateur ne concerne pas la fac (ex: salutations, calculs, questions générales), tu DOIS définir l'intention sur "CHAT".
- Lorsque l'intention est "CHAT", tu dois agir comme une IA experte et générer une réponse naturelle et utile dans "chat_response".

Format JSON exigé :
{{
  "intent": "NOM_INTENTION_OU_CHAT",
  "confidence": 0.99,
  "params": {{
    "nom_prof": "..." // Exemple: uniquement si pertinent
  }},
  "chat_response": "Ta réponse générée ici (si l'intention est CHAT)"
}}

Requête de l'utilisateur : "{text}"
"""
        try:
            # Appel à l'API LLM
            response = self.client.chat_completion(
                messages=[
                    {"role": "system", "content": "Tu es une IA experte qui comprend le langage naturel et renvoie uniquement du JSON valide."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.3
            )
            content = response.choices[0].message.content.strip()
            print(f"[NLP] Réponse brute du LLM : {content}")
            
            # Extraction robuste du JSON via Regex
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                clean_json = json_match.group(0)
            else:
                clean_json = content
                
            result = json.loads(clean_json)
            
            intent = result.get("intent", "UNKNOWN")
            confidence = result.get("confidence", 0.0)
            chat_response = result.get("chat_response", "")
            if "params" in result and isinstance(result["params"], dict):
                params.update(result["params"])
                
        except Exception as e:
            print(f"[NLP] Erreur JSON ou API : {e}")
            intent = "UNKNOWN"
            confidence = 0.0

        return {
            "intent": intent,
            "confidence": confidence,
            "text": text,
            "params": params,
            "chat_response": chat_response
        }

    def generate_response(self, text: str, data: dict) -> str:
        prompt = f"""Tu es Reachy, un robot assistant sympathique de l'université.
L'utilisateur t'a posé cette question : "{text}"

Voici les données renvoyées par le système d'information suite à sa requête :
{json.dumps(data, ensure_ascii=False, indent=2)}

Ta tâche est de formuler une réponse parlée, naturelle et concise pour l'utilisateur, en te basant sur ces données.
Règles :
- Ne mentionne jamais que tu lis des données, du JSON, ou que tu interroges un système.
- Adresse-toi directement à l'utilisateur de manière polie.
- S'il y a une erreur dans les données, explique-le gentiment.
- Sois bref et précis (c'est pour être prononcé à l'oral par un robot).
"""
        try:
            # Appel à l'API LLM pour générer la phrase finale
            response = self.client.chat_completion(
                messages=[
                    {"role": "system", "content": "Tu es Reachy, l'assistant vocal de l'université. Tu dois répondre de manière naturelle et concise."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.5
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[NLP] Erreur de génération de phrase : {e}")
            return "Je suis désolé, j'ai trouvé l'information mais je n'arrive pas à formuler ma réponse correctement."
