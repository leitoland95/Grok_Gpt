from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import os, requests, threading
from openai import OpenAI

API_URL = "https://api.groq.com/openai/v1"
MODEL_NAME = "openai/gpt-oss-20b"   # ajusta al modelo disponible en Groq
API_KEY = os.getenv("GROQ_API_KEY")

client_ia = OpenAI(api_key=API_KEY, base_url=API_URL)

app = FastAPI()

class ChatRequest(BaseModel):
    prompt: str
    image_base64: Optional[str] = None   # ðŸ‘ˆ aquÃ­ recibimos la cadena Base64

@app.post("/chat")
async def chat_endpoint(body: ChatRequest):
    try:
        messages = [{"role": "user", "content": [{"type": "text", "text": body.prompt}]}]

        if body.image_base64:
            messages[0]["content"].append({
                "type": "image_base64",
                "image_base64": {"data": body.image_base64}
            })

        response = client_ia.chat.completions.create(
            model=MODEL_NAME,
            messages=messages
        )

        reply = response.choices[0].message.content
        return {"reply": reply}

    except Exception as e:
        return {"error": str(e)}
        
        
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

threading.Thread(target=keep_alive, daemon=True).start()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))            