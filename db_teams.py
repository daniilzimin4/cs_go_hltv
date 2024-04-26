import sqlite3

# Путь к файлу базы данных SQLite3
from config import DATABASE_PATH
from parse import *


# Функция для добавления команды пользователя в базу данных
def add_team_to_user(chat_id, team_name):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Проверяем, есть ли уже такая команда у пользователя
    cursor.execute("SELECT COUNT(*) FROM users_teams WHERE chat_id = ? AND team_name = ?", (chat_id, team_name))
    count = cursor.fetchone()[0]

    # Если команда еще не добавлена, добавляем её
    if count == 0:
        cursor.execute("INSERT INTO users_teams (chat_id, team_name) VALUES (?, ?)", (chat_id, team_name))
        conn.commit()

    conn.close()


# Функция для удаления команды пользователя в базу данных
def delete_team_from_user(chat_id, team_name):
    print(chat_id, team_name)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users_teams WHERE chat_id = ? AND team_name = ?",
                   (chat_id, team_name))
    conn.commit()
    conn.close()


def get_user_selected_teams(chat_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT team_name FROM users_teams WHERE chat_id = ?",
                   (chat_id,))
    teams = [row[0] for row in cursor.fetchall()]
    conn.close()
    return teams


# Функция для получения списка пользователей, которым будет интересен конкретный матч
def get_users_from_teams(team_a, team_b):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT chat_id FROM users_teams WHERE team_name = ? OR team_name = ?",
                   (team_a, team_b))
    chat_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return chat_ids


def add_teams_to_db():
    teams_data = top30teams()
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Clear existing data
    cursor.execute("DELETE FROM teams")

    for team in teams_data:
        # Extract team data
        team_name = team['name']
        rank = team['rank']
        rank_points = team['rank-points']
        team_id = team['team-id']
        players = team['team-players']

        # Initialize player variables
        player_names = [None] * 5
        player_ids = [None] * 5

        # Populate player variables
        for i, player in enumerate(players):
            player_names[i] = player['name']
            player_ids[i] = player['player-id']

        # Insert team data into the database
        cursor.execute("INSERT INTO teams (name, rank, rank_points, team_id, \
                        player1_name, player1_id, player2_name, player2_id, \
                        player3_name, player3_id, player4_name, player4_id, \
                        player5_name, player5_id) \
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (team_name, rank, rank_points, team_id,
                        player_names[0], player_ids[0],
                        player_names[1], player_ids[1],
                        player_names[2], player_ids[2],
                        player_names[3], player_ids[3],
                        player_names[4], player_ids[4]))

    conn.commit()
    conn.close()


def db_teams_get():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Fetch all team names
    cursor.execute("SELECT name FROM teams")
    team_names = cursor.fetchall()

    conn.close()
    team_names = [name[0] for name in team_names]
    teams_dict = [{'name': team} for team in team_names]
    return teams_dict
