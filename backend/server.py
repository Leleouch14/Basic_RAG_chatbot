import os
import shutil

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ingest import ingest
from vectorstore import collection, delete_chat_chunks
from retrival import retrieve_context
from prompt import SYSTEM_TEMPLATE
from llm import generate_answer
from chat_store import init_db, load_all_chats, save_chat, delete_chat_record

# Boot up the SQLite database
init_db()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/upload")
async def upload_file(file: UploadFile = File(...), chat_id: str = Form(...)):
    save_path = os.path.join(UPLOAD_DIR, f"{chat_id}_{file.filename}")
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    result = ingest(save_path, filename=file.filename, chat_id=chat_id)

    if "error" in result:
        return {"status": "error", **result}

    return {"status": "success", **result}


class AskRequest(BaseModel):
    question: str
    chat_id: str

@app.post("/ask")
async def ask_question(payload: AskRequest):
    context_data = retrieve_context(payload.question, payload.chat_id)

    if context_data is None:
        return {"answer": "I couldn't find this in your uploaded materials.", "sources": [], "grounded": False}

    context_text = "\n\n".join([doc for doc, meta, dist in context_data])
    prompt = SYSTEM_TEMPLATE.format(context=context_text, question=payload.question)
    answer = generate_answer(prompt)

    sources = [{"file": meta["source"], "page": meta["page"]} for doc, meta, dist in context_data]
    return {"answer": answer, "sources": sources, "grounded": True}


# --- CHAT STATE ENDPOINTS ---

class SaveChatRequest(BaseModel):
    chat_id: str
    chat_name: str
    messages: list

@app.get("/chats")
async def api_get_chats():
    return load_all_chats()

@app.post("/chats/save")
async def api_save_chat(payload: SaveChatRequest):
    save_chat(payload.chat_id, payload.chat_name, payload.messages)
    return {"status": "success"}

@app.delete("/chats/{chat_id}")
async def api_delete_chat(chat_id: str):
    # Wipes both the SQL record and the ChromaDB vectors
    delete_chat_record(chat_id)
    delete_chat_chunks(chat_id)
    return {"status": "success"}