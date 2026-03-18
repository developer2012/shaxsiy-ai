import asyncio
import uuid
import json
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import ollama

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

api_keys_db = {}

@app.get("/", response_class=HTMLResponse)
async def read_index():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "index.html fayli topilmadi!"

@app.post("/generate-key")
async def create_key(request: Request):
    data = await request.json()
    new_key = f"sharof-{str(uuid.uuid4())[:8]}"
    api_keys_db[new_key] = data.get("username", "User")
    return {"api_key": new_key}

@app.post("/v1/chat")
async def chat_endpoint(request: Request):
    api_key = request.headers.get("X-Sharof-API-Key")
    if not api_key or api_key not in api_keys_db:
        raise HTTPException(status_code=403, detail="API kalit xato!")

    data = await request.json()
    user_msg = data.get("message")
    
    async def stream_gen():
        client = ollama.AsyncClient()
        try:
            # Render Free uchun llama3.2:1b tavsiya etiladi (eng engili)
            async for chunk in await client.chat(
                model='llama3.2:1b', 
                messages=[{'role': 'user', 'content': user_msg}],
                stream=True
            ):
                if chunk and 'message' in chunk:
                    yield f"data: {json.dumps({'reply': chunk['message']['content']})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(stream_gen(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    # RENDER UCHUN PORTNI DINAMIK OLISH:
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)
