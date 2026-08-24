import httpx

MIDDLEWARE_URL = "http://localhost:3000/api"

class MCPServer:
    async def execute_tool(self, intent: str, params: dict) -> dict:
        async with httpx.AsyncClient() as client:
            try:
                # 1. Recherche prof (M. Tounsi, M. Donati...)
                if intent == "SEARCH_PROF":
                    prof_name = params.get("nom_prof", "")
                    if not prof_name:
                        return {"erreur": "Je n'ai pas compris le nom du professeur. Pouvez-vous répéter ?"}
                    
                    url = f"{MIDDLEWARE_URL}/plannings/professeur/{prof_name}"
                    response = await client.get(url, timeout=5.0)
                    if response.status_code != 200:
                        return {"erreur": f"Erreur lors de la récupération du planning (code {response.status_code})."}
                    return response.json()

                # 2. Dossier étudiant (MIAGE_L3_001, MIAGE_L3_002...)
                elif intent == "GET_DOSSIER":
                    card_id = params.get("id_carte", "")
                    if not card_id:
                        return {
                            "action_requise": "REQUIRE_SCAN",
                            "message": "Veuillez scanner votre carte étudiante devant la caméra pour accéder à votre dossier."
                        }
                    
                    url = f"{MIDDLEWARE_URL}/etudiants/dossier"
                    response = await client.post(url, json={"id_carte": card_id}, timeout=5.0)
                    
                    if response.status_code == 404:
                        return {"erreur": "Aucun dossier trouvé pour cette carte étudiante."}
                    elif response.status_code != 200:
                        return {"erreur": f"Erreur lors de l'accès au dossier (code {response.status_code})."}
                    return response.json()

                # 3. Tous les plannings
                elif intent == "GET_ALL_PLANNINGS":
                    url = f"{MIDDLEWARE_URL}/plannings"
                    response = await client.get(url, timeout=5.0)
                    if response.status_code != 200:
                        return {"erreur": f"Erreur lors de la récupération des plannings (code {response.status_code})."}
                    return response.json()

                # 4. Base de connaissances institutionnelle
                elif intent == "GET_INFO_ADMIN":
                    original_text = params.get("original_text", "")
                    url = f"{MIDDLEWARE_URL}/connaissances/search"
                    response = await client.get(url, params={"q": original_text}, timeout=5.0)
                    if response.status_code != 200:
                        return {"erreur": f"Erreur lors de l'interrogation de la base de connaissances (code {response.status_code})."}
                    return response.json()

                return {"erreur": "Intention non reconnue par le serveur MCP."}

            except httpx.RequestError as e:
                print(f"[MCP] Erreur de requête HTTP: {e}")
                return {"erreur": "Impossible de joindre le middleware Express sur le port 3000."}
            except Exception as e:
                print(f"[MCP] Erreur inattendue: {e}")
                return {"erreur": "Une erreur inattendue s'est produite au sein du MCP."}