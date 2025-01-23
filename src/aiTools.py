from langchain_core.messages import HumanMessage, SystemMessage
import datetime
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from uuid import uuid4
import numpy as np
from langchain.retrievers.multi_query import MultiQueryRetriever
import re

def doc_chunks(content, tabl_name, doc_name, doc_size, doc_date, doc_id):
    """
    Создает объект документа с заданным содержимым и метаданными.

    :param content: Содержимое текста (строка).
    :param tabl_name: Название таблицы (например, идентификатор чата).
    :param doc_name: Имя документа.
    :param doc_size: Размер документа.
    :param doc_date: Дата создания документа.
    :param doc_id: Уникальный идентификатор документа.
    :return: Объект Document с заданными параметрами.
    """
    return Document(
        page_content=content,
        metadata={
            "table": tabl_name,
            "name_doc": doc_name,
            "doc_size": doc_size,
            "doc_date": doc_date,
            "doc_id": doc_id,
        },
    )

def load_docs(document_list, table_id, db, faiss_idx):
    """
    Загружает список документов в базу данных и сохраняет её.

    :param document_list: Список загружаемых документов (например, файлов).
    :param table_id: Идентификатор таблицы/чата.
    :param db: База данных для хранения документов.
    :param faiss_idx: Путь к локальному индексу FAISS.
    """
    for doc in document_list:
        content_doc = doc.read().decode("utf-8")
        name_doc = doc.name
        size_doc = doc.size
        date_doc = str(datetime.date.today())
        type_doc = doc.type
        doc_id = f"doc_id_{str(uuid4())}"

        if type_doc == 'text/plain':
            all_splits = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=600).split_text(content_doc)
            doc_list = [doc_chunks(split, table_id, name_doc, size_doc, date_doc, doc_id) for split in all_splits]

            uuids = [str(uuid4()) for _ in range(len(doc_list))]
            db.add_documents(documents=doc_list, ids=uuids)

    db.save_local(faiss_idx)

def seatch_all_docs(db, table_name):
    """
    Ищет все документы, принадлежащие указанной таблице.

    :param db: База данных, содержащая документы.
    :param table_name: Название таблицы (чата).
    :return: Список метаданных уникальных документов.
    """
    unique_id_doc = set()
    id_to_metadata_map = {}

    for doc_id, document in db.docstore._dict.items():
        if document.metadata and document.metadata.get("table") == str(table_name):
            doc_id = document.metadata.get("doc_id")
            if doc_id:
                unique_id_doc.add(doc_id)
                id_to_metadata_map[doc_id] = document.metadata

    return [id_to_metadata_map[doc_id] for doc_id in unique_id_doc if doc_id in id_to_metadata_map]

def delete_doc_in_bd(db, doc_id, db_path):
    """
    Удаляет документ по идентификатору и обновляет базу данных.

    :param db: База данных, содержащая документы.
    :param doc_id: Идентификатор документа для удаления.
    :param db_path: Путь для сохранения обновленной базы данных.
    """
    chunk_ids_to_delete = []

    for chunk_id, document in db.docstore._dict.items():
        if document.metadata and document.metadata.get("doc_id") == doc_id:
            chunk_ids_to_delete.append(chunk_id)

    for chunk_id in chunk_ids_to_delete:
        del db.docstore._dict[chunk_id]

    if hasattr(db, "index_to_docstore_id") and hasattr(db, "index"):
        indices_to_remove = [
            idx for idx, docstore_id in db.index_to_docstore_id.items()
            if docstore_id in chunk_ids_to_delete
        ]

        if indices_to_remove:
            db.index.remove_ids(np.array(indices_to_remove, dtype=np.int64))

        db.index_to_docstore_id = {
            idx: docstore_id
            for idx, docstore_id in db.index_to_docstore_id.items()
            if docstore_id not in chunk_ids_to_delete
        }

    if not db.docstore._dict:
        db.index_to_docstore_id = {}
        db.index.reset()

    db.save_local(db_path)

def chunks_validator(llm, theme, text):
    """
    Валидирует текстовые чанки на соответствие теме запроса через LLM.

    :param llm: Языковая модель для обработки текста.
    :param theme: Тема, с которой сравнивается текст.
    :param text: Проверяемый текст.
    :return: Процент соответствия текста теме.
    """
    system_message = SystemMessage(content=(
        """
        Ты интеллектуальный ассистент, задача которого — валидировать контент.
        Твоя цель — определять, насколько текст соответствует теме, в процентах.
        Ответ должен быть в формате: n%.
        """
    ))
    human_message = HumanMessage(content=f"Тема запроса: {theme}; Отрывок: {text}")

    messages = [system_message, human_message]
    response = llm.invoke(messages).content
    number_procent = re.findall(r"\d+", response)[0]
    return int(number_procent)

def base_retriver(question, chat_id, llm_s, database, retriver=1, **validator_kwargs):
    """
    Выполняет извлечение документов с использованием выбранного метода.

    :param question: Запрос для поиска.
    :param chat_id: Идентификатор чата.
    :param llm_s: Языковая модель.
    :param database: База данных документов.
    :param retriver: Тип извлекателя (1 — стандартный, 2 — MultiQueryRetriever, 3 — с валидацией).
    :param validator_kwargs: Дополнительные параметры для валидации.
    :return: Список релевантных документов.
    """
    if retriver == 1:
        return database.similarity_search(question, k=10, filter={"table": chat_id})

    elif retriver == 2:
        retriever_from_llm = MultiQueryRetriever.from_llm(
            retriever=database.as_retriever(search_kwargs={"k": 10, "filter": {"table": chat_id}}),
            llm=llm_s
        )
        return retriever_from_llm.invoke(question)

    elif retriver == 3:
        unique_docs = database.similarity_search(question, k=10, filter={"table": chat_id})
        theme = validator_kwargs.get("theme", question)
        return [doc for doc in unique_docs if chunks_validator(llm=llm_s, theme=theme, text=doc) > 70]

def full_rag_request(llm, question, sys_prompt, database, retriver=1, chat_id="default_chat", **validator_kwargs):
    """
    Формирует полный запрос RAG (Retrieve-and-Generate) для получения ответа.

    :param llm: Языковая модель.
    :param question: Запрос пользователя.
    :param sys_prompt: Системное сообщение.
    :param database: База данных для поиска.
    :param retriver: Тип извлекателя.
    :param chat_id: Идентификатор чата.
    :param validator_kwargs: Дополнительные параметры для валидации.
    :return: Ответ на запрос.
    """
    chunks = base_retriver(question, chat_id, llm, database, retriver, **validator_kwargs)
    context = "\n".join([doc.page_content for doc in chunks]) if chunks else ""

    system_message = SystemMessage(content=(
        f"""
        Ты — интеллектуальный помощник. Используй следующий контекст: {context}.
        Ответ должен быть точным, кратким и структурированным.
        """
    ))

    human_message = HumanMessage(content=question)
    messages = [system_message, human_message]

    return llm.invoke(messages).content
