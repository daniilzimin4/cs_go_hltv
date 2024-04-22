import sqlite3

# Путь к файлу базы данных SQLite3
from config import DATABASE_PATH
import requests
from bs4 import BeautifulSoup


# Функция для создания таблиц в базе данных, если их нет
def create_tables():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (user_id INTEGER, 
                       chat_id INTEGER, 
                       team_name TEXT)''')

    # Таблица предстоящих матчей
    cursor.execute('''CREATE TABLE IF NOT EXISTS matches
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       teamA TEXT, 
                       teamB TEXT, 
                       match_time TEXT,
                       event TEXT)''')

    # Таблица всех существующих команд
    cursor.execute('''CREATE TABLE IF NOT EXISTS teams
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                           team TEXT)''')

    conn.commit()
    conn.close()


# Функция для добавления команды пользователя в базу данных
def add_team_to_user(user_id, chat_id, team_name):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (user_id, chat_id, team_name) VALUES (?, ?, ?)", (user_id, chat_id, team_name))
    conn.commit()
    conn.close()


# Функция для удаления команды пользователя в базу данных
def delete_team_from_user(user_id, chat_id, team_name):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    ## написать удаление сттроки user_id, chat_id, team_name
    conn.commit()
    conn.close()


# Функция для получения списка команд, за которыми следит пользователь
def get_user_teams(user_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT team_name FROM users WHERE user_id=?", (user_id,))
    teams = cursor.fetchall()
    conn.close()
    return teams


# Функция для удаления пользователя из базы данных
def delete_user(user_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()


# Функция для парсинга информации о предстоящих матчах
def parse_matches():
    pass
