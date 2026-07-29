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
        
        # Mots-clés directs pour court-circuiter le modèle sur les requêtes évidentes
        self.rules = {
            r"\b(ou est|où est|cherche|salle de|cours avec)\b": "SEARCH_PROF",
            r"\b(notes|dossier|bulletin|absences)\b": "GET_DOSSIER",
            r"\b(emploi du temps|planning)\b": "GET_ALL_PLANNINGS",
            r"\b(inscription|secrétariat|secretariat|règlement|reglement)\b": "GET_INFO_ADMIN"
        }

        # Définition des intentions pour le prompt du LLM
        self.intent_descriptions = {
            "SEARCH_PROF": "Trouver un professeur, chercher un contact enseignant, demander la salle d'un prof.",
            "GET_DOSSIER": "Accéder à son dossier étudiant, ses notes, son bulletin ou ses absences.",
            "GET_ALL_PLANNINGS": "Demander l'emploi du temps, le planning complet ou l'agenda.",
            "GET_INFO_ADMIN": "Demander des informations administratives (inscription, secrétariat, règlement).",
            "CHAT": "L'utilisateur discute, dit bonjour, demande comment tu vas, ou pose une question courante sans rapport avec les autres intentions."
        }

    def classify(self, text: str) -> dict:
        text_lower = text.lower()
        intent = "UNKNOWN"
        confidence = 0.0
        params = {}

        # 1. Vérification par règles (rapide et très robuste pour les phrases typiques)
        for pattern, mapped_intent in self.rules.items():
            if re.search(pattern, text_lower):
                intent = mapped_intent
                confidence = 1.0
                break

        # Extraction d'entité heuristique pour le professeur (au cas où on est passé par les règles)
        if intent == "SEARCH_PROF":
            match = re.search(r"(?:monsieur|madame|professeur|prof|m\.|mr\.|mr|mme|cours de|avec)\s+([a-zA-ZÀ-ÿ\-]+)", text, re.IGNORECASE)
            if match:
                params["nom_prof"] = match.group(1)
            else:
                words = text.split()
                if len(words) > 1:
                    for word in words[1:]:
                        clean_word = re.sub(r'[^a-zA-ZÀ-ÿ\-]', '', word)
                        if clean_word and clean_word[0].isupper() and len(clean_word) > 2:
                            params["nom_prof"] = clean_word
                            break

        chat_response = ""

        # 2. Si aucune règle ne correspond, on affine avec le LLM
        if intent == "UNKNOWN":
            prompt = f"""Tu es Reachy, un robot assistant intelligent de l'université.
Ta tâche est d'analyser la requête et de répondre STRICTEMENT en JSON.

Intentions spécifiques à la fac :
{json.dumps(self.intent_descriptions, ensure_ascii=False, indent=2)}

RÈGLE D'OR : Si la requête de l'utilisateur ne concerne pas la fac (ex: salutations, calculs mathématiques, questions générales, blagues), tu DOIS définir l'intention sur "CHAT".
Lorsque l'intention est "CHAT", tu dois agir comme une vraie IA experte et générer une réponse complète et intelligente dans le champ "chat_response".

Format JSON exigé :
{{
  "intent": "NOM_INTENTION_OU_CHAT",
  "confidence": 0.99,
  "params": {{}},
  "chat_response": "Ta réponse générée ici (si l'intention est CHAT)"
}}

Requête de l'utilisateur : "{text}"
"""
            try:
                # Appel à l'API LLM
                response = self.client.chat_completion(
                    messages=[
                        {"role": "system", "content": "Tu es une IA qui renvoie uniquement du JSON valide."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=400,
                    temperature=0.4
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
                confidence = 0.0

        return {
            "intent": intent,
            "confidence": confidence,
            "text": text,
            "params": params,
            "chat_response": chat_response
        }