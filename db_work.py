import sqlite3

# Путь к файлу базы данных SQLite3
from config import DATABASE_PATH
from parse import *


# Функция для создания таблиц в базе данных, если их нет
def create_tables():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute('''CREATE TABLE IF NOT EXISTS users_teams
                  (chat_id INTEGER, 
                   team_name TEXT)''')

    # Таблица предстоящих матчей
    cursor.execute('''CREATE TABLE IF NOT EXISTS matches
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                   teamA TEXT, 
                   teamB TEXT, 
                   match_time TEXT,
                   date DATE,
                   event TEXT)''')

    # Таблица предстоящих матчей
    cursor.execute('''CREATE TABLE IF NOT EXISTS live_matches
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       teamA TEXT, 
                       teamB TEXT,
                       event TEXT)''')

    # Таблица всех существующих команд
    cursor.execute('''CREATE TABLE IF NOT EXISTS teams 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    name TEXT,
                    rank INTEGER,
                    rank_points INTEGER,
                    team_id INTEGER,
                    player1_name TEXT,
                    player1_id INTEGER,
                    player2_name TEXT,
                    player2_id INTEGER,
                    player3_name TEXT,
                    player3_id INTEGER,
                    player4_name TEXT,
                    player4_id INTEGER,
                    player5_name TEXT,
                    player5_id INTEGER)''')

    # Таблица всех пользователей со статусами
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                  (chat_id INTEGER PRIMARY KEY, 
                   status TEXT)''')

    conn.commit()
    conn.close()


# Добавляет нового пользователя в базу данных
def add_user_to_db(chat_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    request = "INSERT INTO users(chat_id) VALUES(?)"
    cursor.execute(request, (chat_id,))
    conn.commit()
    conn.close()


# Возвращает статус работы с ботом
def get_user_status(chat_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    request = f"SELECT status FROM users WHERE chat_id={chat_id}"
    result = cursor.execute(request).fetchone()
    conn.close()
    return result[0]


# Изменяет статус работы с ботом
def set_user_status(chat_id, status):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    request = "UPDATE users SET status=? WHERE chat_id=?"
    cursor.execute(request, (status, chat_id))
    conn.commit()
    conn.close()


# Обнуляет значение статуса
def reset_user(chat_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    request = "UPDATE users SET status=? WHERE chat_id=?"
    cursor.execute(request, (None, chat_id))
    conn.commit()
    conn.close()
