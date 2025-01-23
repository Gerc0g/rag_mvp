import streamlit as st
from pages.managerPage import manager_page
from pages.chatPage import chat_page
# Сдедать логин либу для стреамлит
from src.initialisateTols import load_database, load_embeddings, load_llm
from src.chatTools import ChatManager
from CONFIG import CONFIG
st.set_page_config(page_title="My App", page_icon="🔥", layout="wide")



######################
# Инициализация кеша #
######################
embending = load_embeddings('cpu')
database = load_database(embending, CONFIG.FAISS_INDEX_PATH)
llm = load_llm(CONFIG.OPENAI_API_KEY, CONFIG.OPENAI_PROXY)

########################
# Инициализация сессии #
########################

if "chat_manager" not in st.session_state:
    st.session_state.chat_manager = ChatManager(CONFIG.CHATLIST_INDEX_PATH)

if "chats" not in st.session_state:
   st.session_state.chats = st.session_state.chat_manager.chats

if "selected_chat" not in st.session_state:
    st.session_state.selected_chat = None

if "messages" not in st.session_state:
        if st.session_state.selected_chat:
            st.session_state.messages = st.session_state.selected_chat.messages
        else:
            st.session_state.messages = []





if __name__ == "__main__":
    pg = st.navigation([
        st.Page(manager_page, title="Manager", icon="💬"),
        st.Page(lambda: chat_page(database, llm, CONFIG.FAISS_INDEX_PATH), title="Chat", icon="📂"),],
        position='sidebar')

    pg.run()