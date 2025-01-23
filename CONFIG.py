import os
from dotenv import load_dotenv

load_dotenv()

class CONFIG:
    FAISS_INDEX_PATH = 'db/mvp_rag_database'
    CHATLIST_INDEX_PATH = "db/chats/chats.json"
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Из .env
    OPENAI_PROXY = os.getenv("OPENAI_PROXY")      # Из .env
    EMBEDDINGS_DEVICE = 'cpu'
