import sqlite3

# Путь к файлу базы данных SQLite3
from config import DATABASE_PATH
from parse import *


def update_upcoming_matches(matches):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Удаление существующих записей
    cursor.execute("DELETE FROM matches")
    # Вставка новых записей
    for match in matches:
        if match['team1'] is None or match['team2'] is None:
            continue
        cursor.execute("INSERT INTO matches (teamA, teamB, match_time, date, event) VALUES (?, ?, ?, ?, ?)",
                       (match['team1'].decode('utf-8'), match['team2'].decode('utf-8'), match['time'], match['date'],
                        match['event'].decode('utf-8')))
    conn.commit()
    conn.close()


def update_live_matches(matches):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM live_matches")
    for match in matches:
        if match['team1'] is None or match['team2'] is None:
            continue
        cursor.execute("INSERT INTO live_matches (teamA, teamB, event) VALUES (?, ?, ?)",
                       (match['team1'].decode('utf-8'), match['team2'].decode('utf-8'),
                        match['event'].decode('utf-8')))
    conn.commit()
    conn.close()


# Функция для парсинга информации о предстоящих матчах
def db_parse_matches():
    matches = get_upcoming_matches()
    live_matches = get_live_matches()
    update_upcoming_matches(matches)
    update_live_matches(live_matches)


def get_upcoming_matches_from_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT teamA, teamB, match_time, date, event FROM matches LIMIT 15")
    matches = cursor.fetchall()
    conn.close()
    return matches


def get_live_matches_from_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT teamA, teamB, event FROM live_matches LIMIT 15")
    matches = cursor.fetchall()
    conn.close()
    return matches


# Функция для форматирования предстоящих матчей в текстовый вид
def format_matches(matches):
    formatted_matches = ""
    for match in matches:
        formatted_matches += f"{match[0]} vs {match[1]}\n"
        formatted_matches += f"Event: {match[4]}\n"
        formatted_matches += f"Date: {match[3]}, Time: {match[2]}\n\n"
    return formatted_matches


# Функция для форматирования предстоящих матчей в текстовый вид
def format_live_matches(matches):
    formatted_matches = ""
    for match in matches:
        formatted_matches += f"{match[0]} vs {match[1]}\n"
        formatted_matches += f"Event: {match[2]}\n\n"
    return formatted_matches
