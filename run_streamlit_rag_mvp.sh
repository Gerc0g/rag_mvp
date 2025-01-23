#!/bin/bash

# Останавливаем и удаляем контейнер, если он уже существует
docker stop streamlit_rag_app || true
docker rm streamlit_rag_app || true

# Собираем новый Docker-образ
docker build -t streamlit_rag_app .

# Запускаем контейнер с маппингом портов и флагом -d для работы в фоне
docker run -d -p 8501:8501 --name streamlit_rag_app streamlit_rag_app

# Получаем внешний IP-адрес сервера
#SERVER_IP=$(curl -s http://checkip.amazonaws.com)

# Выводим сообщение с реальным IP-адресом
echo "Streamlit app is running and accessible via http://10.234.234.222:8501"
