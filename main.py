# server.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import os, requests
import uvicorn
import threading

API_URL = "https://api.groq.com/v1/infer"
MODEL_NAME = "your-multimodal-model"  # reemplaza por el modelo Groq
API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise RuntimeError("GROQ_API_KEY no encontrada en variables de entorno")

app = FastAPI()

class ChatRequest(BaseModel):
    messages: list[str]
    image_url: HttpUrl | None = None
    
@app.get("/")
def root():
    return {"status": 200}    

@app.post("/chat")
def chat(req: ChatRequest):
    payload = {
        "model": MODEL_NAME,
        "input": {
            "messages": req.messages
        }
    }
    if req.image_url:
        payload["input"]["image_url"] = str(req.image_url)

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    resp = requests.post(API_URL, json=payload, headers=headers, timeout=30)
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Upstream error: {resp.text}")
    return resp.json()
    
def keep_alive():
    url = "https://srelemium-scraper-1.onrender.com"
    if not url:
        log("No se encontró RENDEREXTERNALURL, keep_alive desactivado")
        return
    while True:
        try:
            requests.get(url, timeout=10)
            log(f"Ping a {url} para mantener vivo el servicio")
        except Exception as e:
            log(f"Error en keep_alive: {e}")
        time.sleep(60)

threading.Thread(target=keep_alive, daemon=True).start()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))    