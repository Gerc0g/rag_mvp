import streamlit as st
from src.aiTools import load_docs, seatch_all_docs, delete_doc_in_bd, full_rag_request

def chat_page(db, llm_model, index_path):

    ########################################
    # Параметры чата и загрузка документов #
    ########################################
    with st.sidebar:
        st.warning(f'Текущий чат - {st.session_state.selected_chat.name if st.session_state.selected_chat else "Чат не выбран"}')
        if st.session_state.selected_chat != None:
            rag_deep = st.select_slider(
            "Глубина поиска по документам",
            options=[
                "1",
                "2",
                "3",],)

            st.title("Загрузка файла")
            uploaded_files = st.file_uploader(label = 'Загрузка файла', type = [".txt"], accept_multiple_files=True, label_visibility='collapsed')
            if st.button('Загрузить', disabled=bool(False if uploaded_files != [] else True),use_container_width=True):
                load_docs(uploaded_files, st.session_state.selected_chat.database_id, db, index_path)

            st.title("Список файлов")
            stats = seatch_all_docs(db, st.session_state.selected_chat.database_id)
            for idx, doc in enumerate(stats):
                col1, col2, col3, col4 = st.columns([2, 1, 2, 3])
                col1.write(doc["name_doc"])
                col2.write(doc["doc_size"])
                col3.write(doc["doc_date"])
                if col4.button('Удалить', use_container_width=True, key=f"Data_button-{idx}"):
                    delete_doc_in_bd(db, doc["doc_id"], index_path)
                    st.rerun()

    #############
    # Окно чата #
    #############
    if st.session_state.selected_chat is not None:
        for message in st.session_state.selected_chat.messages:
            if not (message["role"] == "pass" or message["content"] == "pass"):
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        if prompt := st.chat_input("Введите сообщение:"):
            user_message = {"role": "user", "content": prompt}
            st.session_state.chat_manager.add_message_to_chat(st.session_state.selected_chat.id, user_message)


            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                response = full_rag_request(
                                            llm=llm_model,
                                            question=prompt,
                                            sys_prompt = st.session_state.selected_chat.system_prompt,
                                            database=db,
                                            retriver=int(rag_deep),
                                            chat_id=st.session_state.selected_chat.database_id
                                        )
                st.markdown(response)

            st.session_state.chat_manager.add_message_to_chat(st.session_state.selected_chat.id, {"role": "assistant", "content": response})
