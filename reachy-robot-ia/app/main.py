from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

from app.services.stt_service import STTService
from app.services.nlp_service import NLPService
from app.mcp.mcp_server import MCPServer

services = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Chargement unique des modèles au démarrage du serveur
    services["stt"] = STTService(model_size="small")
    services["nlp"] = NLPService()
    services["mcp"] = MCPServer()
    print("[FASTAPI] Cœur IA prêt !")
    yield
    services.clear()

app = FastAPI(title="Reachy Mini - Serveur IA", lifespan=lifespan)

class AnalysisRequest(BaseModel):
    text: str
    params: dict = {}

@app.post("/api/v1/stt")
async def process_stt(file: UploadFile = File(...)):
    audio_bytes = await file.read()
    transcription = services["stt"].transcribe(audio_bytes)
    return {"transcription": transcription}

@app.post("/api/v1/process")
async def process_pipeline(req: AnalysisRequest):
    nlp_result = services["nlp"].classify(req.text)
    
    # Fusion des paramètres de la requête et de ceux extraits par le NLP
    params = req.params.copy()
    if "params" in nlp_result:
        params.update(nlp_result["params"])
    params["original_text"] = req.text
        
    if nlp_result["intent"] == "CHAT":
        # Si c'est une simple discussion, on ne passe pas par MCP
        mcp_result = {
            "response": nlp_result.get("chat_response", "Bonjour ! Je suis Reachy, comment puis-je t'aider ?")
        }
    else:
        # On exécute l'outil via MCP
        mcp_result = await services["mcp"].execute_tool(nlp_result["intent"], params)
    
    return {
        "analysis": nlp_result,
        "mcp_response": mcp_result
    }