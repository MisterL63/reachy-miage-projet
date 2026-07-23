from transformers import pipeline

class NLPService:
    def __init__(self):
        print("[NLP] Chargement du modèle de classification...")
        self.classifier = pipeline(
            "zero-shot-classification",
            model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
        )
        # Intentions alignées sur ton middleware Express
        self.candidate_labels = [
            "demander la localisation d'un professeur ou d'un cours",
            "consulter le dossier etudiant ou les notes",
            "demander tout l'emploi du temps"
        ]

    def classify(self, text: str) -> dict:
        res = self.classifier(text, self.candidate_labels)
        top_label = res["labels"][0]
        
        mapping = {
            "demander la localisation d'un professeur ou d'un cours": "SEARCH_PROF",
            "consulter le dossier etudiant ou les notes": "GET_DOSSIER",
            "demander tout l'emploi du temps": "GET_ALL_PLANNINGS"
        }

        return {
            "intent": mapping.get(top_label, "UNKNOWN"),
            "confidence": round(res["scores"][0], 2),
            "text": text
        }