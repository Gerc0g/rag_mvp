import streamlit as st
def manager_page():

    select_chunk, create_chunk = st.columns([0.3, 0.7])

    ################
    # Список чатов #
    ################
    with select_chunk:
        with st.container(border=True):
            st.title("Список чатов")

            if not st.session_state.chats:
                st.warning("Чаты отсутствуют")
            else:
                st.warning(
                    f"Текущий чат - {st.session_state.selected_chat.name if st.session_state.selected_chat else 'Чат не выбран'}"
                )

                for i, chat in enumerate(st.session_state.chats):
                    if st.button(chat.name, key=f"chat_button_{i}", use_container_width=True):
                        st.session_state.selected_chat = chat
                        st.session_state.messages = st.session_state.selected_chat.messages
                        st.rerun()
    #################
    # Создание чата #
    #################
    with create_chunk:
        with st.container(border=True):
            st.title("Создание чата")
            chat_name = st.text_input("Название чата", value='', placeholder="Введите имя чата...")
            chat_description = st.text_area("Описание", value='', placeholder="Введите описание чата...")
            sys_prompt = st.text_area("Системный промпт", value='', height=220, placeholder="Введите системный промпт...")

            all_fields_filled = bool(chat_name.strip() and chat_description.strip() and sys_prompt.strip())

            if st.button("Создать чат", disabled=not all_fields_filled, use_container_width=True):
                st.session_state.chat_manager.add_chat(chat_name, chat_description, sys_prompt)
                st.session_state.chats = st.session_state.chat_manager.chats
                st.rerun()

            st.title("Удалить чат")
            chat_delete_select = st.selectbox(
                "",
                options=[f"{item.name} - {item.id}" for item in st.session_state.chats] if st.session_state.chats else [],
                placeholder="Выберите чат который хотите удалить...",
                label_visibility="hidden",
            )

            left_col, right_col = st.columns([0.7, 0.3])

            with left_col:
                if chat_delete_select:
                    selected_id = chat_delete_select.split(" - ")[1]
                    selected_chat = st.session_state.chat_manager.get_chat_by_id(selected_id)
                    if selected_chat:
                        st.write(f"Описание: {selected_chat.description}")

            with right_col:
                if st.button("Удалить", use_container_width=True, disabled=not bool(chat_delete_select)):
                    selected_id = chat_delete_select.split(" - ")[1]
                    st.session_state.chat_manager.delete_chat(selected_id)
                    st.session_state.chats = st.session_state.chat_manager.chats
                    if st.session_state.selected_chat and st.session_state.selected_chat.id == selected_id:
                        st.session_state.selected_chat = None
                    st.rerun()
