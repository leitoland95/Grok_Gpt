###### DEPENDENCIAS ##############

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import os, requests, threading
from openai import OpenAI
import uvicorn
from groq import Groq

###### VARIABLES #################


MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct"   # ajusta al modelo disponible en Groq

client_ia = Groq(api_key=os.environ.get("GROQ_API_KEY"))

app = FastAPI()

exec_logs = []

###### CLASES ####################

class ChatRequest(BaseModel):
    prompt: str
    image_base64: Optional[str] = None   # ðŸ‘ˆ aquÃ­ recibimos la cadena Base64
    
    
###### FUNCIONES #################

def log(msg: str):
    exec_logs.append(msg)
    print(msg)
    
def keep_alive():
    url = "https://grok-gpt.onrender.com"
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
        
###### ENDPOINTS #################

@app.get("/")
def root():
    return {"status":200}
    
@app.get("/logs")
def save_logs():
    return exec_logs    
    
from fastapi import FastAPI
from pydantic import BaseModel
import os

app = FastAPI()

MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct"

# Variable global para persistencia
conversation_id = None

class ChatRequest(BaseModel):
    prompt: str
    image_base64: str | None = None

@app.post("/chat")
async def chat_endpoint(body: ChatRequest):
    global conversation_id
    try:
        # Construcción de mensajes
        if not body.image_base64:
            messages = [{
                "role": "user",
                "content": body.prompt
            }]
        else:
            data_url = f"data:image/jpeg;base64,{body.image_base64}"
            messages = [{
                "role": "user",
                "content": [
                    {"type": "text", "text": body.prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": data_url}
                    }
                ]
            }]

        # Enviar petición con conversation_id si existe
        response = client_ia.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            conversation_id=conversation_id if conversation_id else None
        )

        # Actualizar conversation_id con el que devuelve la API
        conversation_id = getattr(response, "conversation_id", conversation_id)

        reply = response.choices[0].message.content
        return {
            "reply": reply,
            "conversation_id": conversation_id
        }

    except Exception as e:
        return {"error": str(e)}
        
        
###### EJECUCIÓN #################

threading.Thread(target=keep_alive, daemon=True).start()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))            