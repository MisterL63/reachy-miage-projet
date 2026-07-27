import re
from transformers import pipeline

class NLPService:
    def __init__(self):
        print("[NLP] Chargement du modèle de classification...")
        self.classifier = pipeline(
            "zero-shot-classification",
            model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
        )
        
        # Mots-clés directs pour court-circuiter le modèle sur les requêtes évidentes
        self.rules = {
            r"\b(ou est|où est|cherche|salle de|cours avec)\b": "SEARCH_PROF",
            r"\b(notes|dossier|bulletin|absences)\b": "GET_DOSSIER",
            r"\b(emploi du temps|planning)\b": "GET_ALL_PLANNINGS",
            r"\b(inscription|secrétariat|secretariat|règlement|reglement)\b": "GET_INFO_ADMIN"
        }

        # Moins de labels pour éviter que la probabilité (softmax) ne se divise
        # entre des labels similaires
        self.intent_mapping = {
            "trouver un professeur": "SEARCH_PROF",
            "dossier étudiant": "GET_DOSSIER",
            "planning complet": "GET_ALL_PLANNINGS",
            "informations administratives": "GET_INFO_ADMIN"
        }
        self.candidate_labels = list(self.intent_mapping.keys())

    def classify(self, text: str) -> dict:
        text_lower = text.lower()
        intent = "UNKNOWN"
        confidence = 0.0

        # 1. Vérification par règles (rapide et très robuste pour les phrases typiques)
        for pattern, mapped_intent in self.rules.items():
            if re.search(pattern, text_lower):
                intent = mapped_intent
                confidence = 1.0
                break

        # 2. Si aucune règle ne correspond, on utilise le modèle IA Zero-Shot
        if intent == "UNKNOWN":
            res = self.classifier(
                text, 
                self.candidate_labels, 
                hypothesis_template="Le sujet de cette phrase est : {}."
            )
            top_label = res["labels"][0]
            intent = self.intent_mapping.get(top_label, "UNKNOWN")
            confidence = round(res["scores"][0], 2)
            
        params = {}
        
        # Extraction d'entité beaucoup plus flexible pour le professeur
        if intent == "SEARCH_PROF":
            # 1. Chercher avec un préfixe (M., Mr., Mme, Prof, avec, de...)
            match = re.search(r"(?:monsieur|madame|professeur|prof|m\.|mr\.|mr|mme|cours de|avec)\s+([a-zA-ZÀ-ÿ\-]+)", text, re.IGNORECASE)
            if match:
                params["nom_prof"] = match.group(1)
            else:
                # 2. Heuristique : chercher un mot avec une majuscule (Nom propre) qui n'est pas le 1er mot
                words = text.split()
                if len(words) > 1:
                    for word in words[1:]:
                        clean_word = re.sub(r'[^a-zA-ZÀ-ÿ\-]', '', word)
                        if clean_word and clean_word[0].isupper() and len(clean_word) > 2:
                            params["nom_prof"] = clean_word
                            break

        return {
            "intent": intent,
            "confidence": confidence,
            "text": text,
            "params": params
        }