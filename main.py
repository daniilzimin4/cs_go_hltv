import sqlite3

import telebot
import time
from datetime import datetime, timedelta

# Импорт настроек и функций для работы с базой данных
from config import TOKEN
from db_work import create_tables, add_team_to_user, delete_team_from_user, get_user_teams, parse_matches, DATABASE_PATH

# Инициализация бота
bot = telebot.TeleBot(TOKEN)


# Функция для отправки уведомлений о предстоящих матчах
def send_match_notifications():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Получение всех пользователей и их команд
    cursor.execute("SELECT chat_id, team_name FROM users")
    users = cursor.fetchall()

    # Получение всех предстоящих матчей
    cursor.execute("SELECT home_team, away_team, match_time FROM matches")
    matches = cursor.fetchall()

    conn.close()

    for user in users:
        chat_id = user[0]
        team_name = user[1]
        relevant_matches = [match for match in matches if team_name in match[0] or team_name in match[1]]

        for match in relevant_matches:
            match_time = datetime.strptime(match[2], "%Y-%m-%d %H:%M")
            time_difference = match_time - datetime.now()

            # Отправка уведомления за 1 час и за 24 часа до начала матча
            if timedelta(hours=1) < time_difference < timedelta(hours=2):
                bot.send_message(chat_id, f"Через час начнется матч: {match[0]} - {match[1]}")
            elif timedelta(hours=23) < time_difference < timedelta(days=1):
                bot.send_message(chat_id, f"Завтра в это время будет матч: {match[0]} - {match[1]}")


# Обработка команды /start
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, "Привет! Я бот киберспортивных матчей по CS2. Используй /help для получения списка команд.")


# Обработка команды /help
@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id, "Список доступных команд:\n"
                                      "/all_teams - Посмотреть все команды, которые можно начать отслеживать\n"
                                      "/add_team - Добавить команду для отслеживания\n"
                                      "/remove_team - Удалить команду из списка отслеживания\n"
                                      "/my_teams - Посмотреть список отслеживаемых команд\n"
                                      "/all_matches - Посмотреть все предстоящие матчи\n"
                                      "/league_matches - Посмотреть предстоящие матчи в определенной лиге")

# Обработка команды /all_teams
@bot.message_handler(commands=['all_teams'])
def all_teams_command(message):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Получение всех команд
    cursor.execute("SELECT team_name FROM teams")
    teams = cursor.fetchall()
    bot.send_message(message.chat.id, "Список команд, о которых можно получать уведомления:" + "\n".join(teams))


# Обработка команды /add_team
@bot.message_handler(commands=['add_team'])
def add_team_command(message):
    bot.send_message(message.chat.id, "Введите название команды, которую хотите добавить:")
    bot.register_next_step_handler(message, add_team)


def add_team(message):
    team_name = message.text.strip().lower()
    chat_id = message.chat.id
    add_team_to_user(message.from_user.id, chat_id, team_name)
    bot.send_message(chat_id, f"Команда {team_name} добавлена в список отслеживаемых.")


# Обработка команды /remove_team
@bot.message_handler(commands=['remove_team'])
def remove_team_command(message):
    bot.send_message(message.chat.id, "Введите название команды, которую хотите удалить:")
    bot.register_next_step_handler(message, remove_team)


def remove_team(message):
    team_name = message.text.strip().lower()
    chat_id = message.chat.id
    delete_team_from_user(message.from_user.id, chat_id, team_name)
    bot.send_message(chat_id, f"Команда {team_name} удалена из списка отслеживаемых.")


# Обработка команды /my_teams
@bot.message_handler(commands=['my_teams'])
def my_teams_command(message):
    chat_id = message.chat.id
    user_teams = get_user_teams(message.from_user.id)
    if user_teams:
        bot.send_message(chat_id, "Ваши отслеживаемые команды:\n" + "\n".join(user_teams))
    else:
        bot.send_message(chat_id, "Вы не отслеживаете ни одну команду.")


# Обработка команды /all_matches
@bot.message_handler(commands=['all_matches'])
def all_matches_command(message):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT teamA, teamB, match_time FROM matches")
    ## написать выбор всех матчей, которые спарсены и есть в бд, и старт в будущем, только будущие матчи здесь
    ## то есть запрос к бд
    matches = cursor.fetchall()
    conn.close()

    if matches:
        bot.send_message(message.chat.id, "Предстоящие матчи:\n" +
                         "\n".join(f"{match[0]} - {match[1]} ({match[2]})" for match in matches))
    else:
        bot.send_message(message.chat.id, "На данный момент нет предстоящих матчей.")


# Обработка команды /league_matches
@bot.message_handler(commands=['league_matches'])
def league_matches_command(message):
    bot.send_message(message.chat.id, "Введите название турнира (например, ESL PRO LEAGUE 19):")
    bot.register_next_step_handler(message, league_matches)


def league_matches(message):
    league_name = message.text.strip()
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT home_team, away_team, match_time FROM matches WHERE league=?", (league_name,))
    ## то же самое, исправить запрос нужно, мб добавить в бд новую инфу с лигой
    matches = cursor.fetchall()
    conn.close()

    if matches:
        bot.send_message(message.chat.id, f"Предстоящие матчи в турнире {league_name}:\n" +
                         "\n".join(f"{match[0]} - {match[1]} ({match[2]})" for match in matches))
    else:
        bot.send_message(message.chat.id, f"На данный момент нет предстоящих матчей в турнире {league_name}.")


create_tables()
bot.polling()

# пока что раз в 3600 секунд запускается и парсит всю страницу с матчами
# в будущем можно сделать, чтобы обновлял страницу каждые 30 секунд
# нужно еще хранить таблицу в которой будет типо такая тема, уведомляли ли мы пользователя о таком-то матче или нет, чтобы уведомлять
while True:
    parse_matches()
    send_match_notifications()
    time.sleep(3600)  # Парсинг каждый час
