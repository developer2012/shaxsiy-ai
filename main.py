import asyncio
import uuid
import json
import os
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import ollama

app = FastAPI()

# Barcha portlardan ulanishga ruxsat berish
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# API kalitlarni vaqtinchalik saqlash
api_keys_db = {}

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/generate-key")
async def create_key(request: Request):
    data = await request.json()
    new_key = f"sharof-{str(uuid.uuid4())[:8]}"
    api_keys_db[new_key] = data.get("username", "User")
    return {"api_key": new_key}

# DIQQAT: Manzil aynan /v1/chat bo'lishi kerak
@app.post("/v1/chat")
async def chat_endpoint(request: Request):
    # API keyni tekshirish
    api_key = request.headers.get("X-Sharof-API-Key")
    if not api_key or api_key not in api_keys_db:
        raise HTTPException(status_code=403, detail="API kalit xato!")

    data = await request.json()
    user_msg = data.get("message")
    
    async def stream_gen():
        client = ollama.AsyncClient()
        try:
            # Eski: model='gemma:2b'
# Yangi (sizdagi model):
            async for chunk in await client.chat(
    model='llama3', 
    messages=[{'role': 'user', 'content': user_msg}],
    stream=True
):
                yield f"data: {json.dumps({'reply': chunk['message']['content']})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(stream_gen(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)