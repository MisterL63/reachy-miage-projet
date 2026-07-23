import httpx

MIDDLEWARE_URL = "http://localhost:3000/api"

class MCPServer:
    async def execute_tool(self, intent: str, params: dict) -> dict:
        async with httpx.AsyncClient() as client:
            try:
                # 1. Recherche prof (M. Tounsi, M. Donati...)
                if intent == "SEARCH_PROF":
                    prof_name = params.get("nom_prof", "")
                    url = f"{MIDDLEWARE_URL}/plannings/professeur/{prof_name}"
                    response = await client.get(url)
                    return response.json()

                # 2. Dossier étudiant (MIAGE_L3_001, MIAGE_L3_002...)
                elif intent == "GET_DOSSIER":
                    card_id = params.get("id_carte", "")
                    url = f"{MIDDLEWARE_URL}/etudiants/dossier"
                    response = await client.post(url, json={"id_carte": card_id})
                    return response.json()

                # 3. Tous les plannings
                elif intent == "GET_ALL_PLANNINGS":
                    url = f"{MIDDLEWARE_URL}/plannings"
                    response = await client.get(url)
                    return response.json()

                return {"erreur": "Intention non reconnue par le serveur MCP"}

            except httpx.RequestError:
                return {"erreur": "Impossible de joindre le middleware Express sur le port 3000"}