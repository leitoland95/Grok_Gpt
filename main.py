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
    
@app.post("/chat")
async def chat_endpoint(body: ChatRequest):
    try:
        # Si no hay imagen  mensaje simple
        if not body.image_base64:
            messages = [{
                "role": "user",
                "content": body.prompt
            }]
        else:
            # Construir data URL
            data_url = f"data:image/jpeg;base64,{body.image_base64}"

            # Mensaje multimodal correcto para Groq
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

        response = client_ia.chat.completions.create(
            model=MODEL_NAME,
            messages=messages
        )

        reply = response.choices[0].message.content
        return {"reply": reply}

    except Exception as e:
        return {"error": str(e)}
        
        
###### EJECUCIÓN #################

threading.Thread(target=keep_alive, daemon=True).start()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))            