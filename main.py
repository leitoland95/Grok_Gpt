# server.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import os, requests
import uvicorn
import threading
from openai import OpenAI

API_URL = "https://api.groq.com/openai/v1"
MODEL_NAME = "openai/gpt-oss-20b"  # reemplaza por el modelo Groq
API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise RuntimeError("GROQ_API_KEY no encontrada en variables de entorno")

app = FastAPI()


@app.get("/")
def root():
    return {"status": 200}    

@app.post("/chat")
async def chat_endpoint(prompt, image):
    try:
        # Construir mensajes: texto + imagen si existe
        messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]

        if image != None
        	upload_resp = openai.File.create(
        file=image,
        purpose="vision"  # Indica que el archivo se usará para visión
    )
    
            messages[0]["content"].append({"type": "image_file", "image_file": {"file_id": upload_resp.id}})

        response = client_ia.chat.completions.create(
            model="openai/gpt-oss-20b",  # ajusta al modelo que Groq soporte
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