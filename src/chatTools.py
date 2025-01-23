import os
import json
import uuid

class Chat:
    """
    Класс для представления чата. Содержит основные свойства чата и методы
    для преобразования его в словарь и создания из словаря.
    """
    def __init__(self, name, description, system_prompt, id=None, database_id=None, messages=None):
        """
        Инициализация чата.
        
        :param name: Имя чата.
        :param description: Описание чата.
        :param system_prompt: Системное сообщение для чата.
        :param id: Уникальный идентификатор чата. Если не задан, генерируется автоматически.
        :param database_id: Идентификатор базы данных чата. Если не задан, генерируется автоматически.
        :param messages: Список сообщений чата. Если не задан, используется сообщение по умолчанию.
        """
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        self.database_id = database_id or f"{name}_{str(uuid.uuid4())}"
        self.messages = messages if messages is not None else [{"role": "pass", "content": "pass"}]

    def to_dict(self):
        """
        Преобразует объект чата в словарь.
        :return: Словарь с данными чата.
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "system_prompt": self.system_prompt,
            "database_id": self.database_id,
            "messages": self.messages
        }

    @staticmethod
    def from_dict(data):
        """
        Создает объект чата из словаря.
        
        :param data: Словарь с данными чата.
        :return: Объект Chat.
        """
        return Chat(
            id=data.get("id"),
            name=data["name"],
            description=data["description"],
            system_prompt=data["system_prompt"],
            database_id=data["database_id"],
            messages=data.get("messages", [])
        )


class ChatManager:
    """
    Менеджер для управления чатами. Содержит методы для загрузки, сохранения,
    добавления, удаления и обновления чатов.
    """
    def __init__(self, path):
        """
        Инициализация менеджера чатов.
        
        :param path: Путь к файлу, где хранятся чаты.
        """
        self.path = path
        self.chats = self.load_chats()

    def load_chats(self):
        """
        Загружает чаты из файла. Если файл отсутствует или пуст, возвращает пустой список.
        
        :return: Список объектов Chat.
        """
        if not os.path.exists(self.path) or os.stat(self.path).st_size == 0:
            return []
        with open(self.path, "r") as f:
            chat_dicts = json.load(f)
            return [Chat.from_dict(chat) for chat in chat_dicts]

    def save_chats(self):
        """
        Сохраняет чаты в файл. Если директория не существует, создает её.
        """
        directory = os.path.dirname(self.path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(self.path, "w") as f:
            json.dump([chat.to_dict() for chat in self.chats], f, ensure_ascii=False, indent=4)
    def add_chat(self, name, description, system_prompt):
        """
        Добавляет новый чат и сохраняет изменения.
        
        :param name: Имя чата.
        :param description: Описание чата.
        :param system_prompt: Системное сообщение для чата.
        """
        new_chat = Chat(name, description, system_prompt)
        self.chats.append(new_chat)
        self.save_chats()

    def delete_chat(self, chat_id):
        """
        Удаляет чат по его ID и сохраняет изменения.
        
        :param chat_id: Уникальный идентификатор чата для удаления.
        """
        self.chats = [chat for chat in self.chats if chat.id != chat_id]
        self.save_chats()

    def get_chat_by_id(self, chat_id):
        """
        Возвращает чат по его ID.
        
        :param chat_id: Уникальный идентификатор чата.
        :return: Объект Chat или None, если чат не найден.
        """
        return next((chat for chat in self.chats if chat.id == chat_id), None)

    def add_message_to_chat(self, chat_id, message):
        """
        Добавляет сообщение в чат и сохраняет изменения.
        
        :param chat_id: Уникальный идентификатор чата.
        :param message: Сообщение, которое нужно добавить (формат: словарь с role и content).
        """
        chat = self.get_chat_by_id(chat_id)
        if chat:
            chat.messages.append(message)
            self.save_chats()
        else:
            raise ValueError(f"Чат с ID {chat_id} не найден")

    def update_chat(self, chat_id, name=None, description=None, system_prompt=None):
        """
        Обновляет параметры чата (имя, описание, системное сообщение) и сохраняет изменения.
        
        :param chat_id: Уникальный идентификатор чата.
        :param name: Новое имя чата (опционально).
        :param description: Новое описание чата (опционально).
        :param system_prompt: Новое системное сообщение (опционально).
        """
        chat = self.get_chat_by_id(chat_id)
        if chat:
            if name:
                chat.name = name
            if description:
                chat.description = description
            if system_prompt:
                chat.system_prompt = system_prompt
            self.save_chats()
        else:
            raise ValueError(f"Чат с ID {chat_id} не найден")
