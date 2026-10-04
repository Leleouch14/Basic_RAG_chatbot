import requests

BACKEND_URL = "http://127.0.0.1:8000"

def upload_document(file, chat_id: str):
    files = {"file": (file.name, file.getvalue(), file.type)}
    data = {"chat_id": chat_id}
    try:
        response = requests.post(f"{BACKEND_URL}/upload", files=files, data=data)
        response.raise_for_status()
        return {"success": True, "data": response.json()}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}

def ask_backend(question: str, chat_id: str):
    payload = {"question": question, "chat_id": chat_id}
    try:
        response = requests.post(f"{BACKEND_URL}/ask", json=payload)
        response.raise_for_status()
        return {"success": True, "data": response.json()}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}

def fetch_all_chats():
    try:
        response = requests.get(f"{BACKEND_URL}/chats")
        response.raise_for_status()
        return response.json()
    except:
        return {}

def sync_chat_state(chat_id: str, chat_name: str, messages: list):
    payload = {"chat_id": chat_id, "chat_name": chat_name, "messages": messages}
    try:
        requests.post(f"{BACKEND_URL}/chats/save", json=payload)
    except:
        pass

def purge_chat(chat_id: str):
    try:
        requests.delete(f"{BACKEND_URL}/chats/{chat_id}")
    except:
        pass