from langchain_huggingface import HuggingFaceEmbeddings
import streamlit as st
from langchain_community.vectorstores import FAISS
import os
from langchain_openai import ChatOpenAI


@st.cache_resource
def load_embeddings(type):
    """
    Загружает модель эмбеддингов HuggingFace для заданного устройства (CPU или GPU).

    :param type: Тип устройства для загрузки модели ('cpu' или 'cuda').
    :return: Экземпляр HuggingFaceEmbeddings.
    """
    model_id = 'intfloat/multilingual-e5-large'
    if type == 'cpu':
        model_kwargs = {'device': 'cpu'}
    else:
        model_kwargs = {'device': 'cuda'}
    embeddings = HuggingFaceEmbeddings(
        model_name=model_id,
        model_kwargs=model_kwargs
    )
    return embeddings


@st.cache_resource
def load_database(_embedding, faiss_idx):
    """
    Загружает или создает локальную базу данных FAISS для хранения векторных представлений.

    :param _embedding: Экземпляр модели эмбеддингов.
    :param faiss_idx: Путь к локальному индексу FAISS.
    :return: Экземпляр FAISS базы данных.
    """
    if os.path.exists(faiss_idx) and os.path.isdir(faiss_idx):
        db = FAISS.load_local(faiss_idx, _embedding, allow_dangerous_deserialization=True)
    else:
        db = FAISS.from_texts("Hello pipl", _embedding)
        db.save_local(faiss_idx)
    return db


@st.cache_resource
def load_llm(api_key, proxy):
    """
    Загружает языковую модель OpenAI через LangChain с заданными настройками.

    :param api_key: API ключ для доступа к OpenAI.
    :param proxy: Прокси-сервер для запросов к OpenAI.
    :return: Экземпляр ChatOpenAI.
    """
    llm = ChatOpenAI(
        model="gpt-4o",
        api_key=api_key,
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        openai_proxy=proxy,
        streaming=True
    )
    return llm
