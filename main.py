import time

import telebot
import logging
import threading

# Импорт настроек и функций для работы с базой данных
from config import TOKEN
from db_work import *
from messages import *
from keyboards import *
from db_teams import *
from db_matches import *

# Инициализация бота
bot = telebot.TeleBot(TOKEN)

logging.basicConfig(filename="log.log", level=logging.INFO)
log = logging.getLogger("Bot")
log.info("Start")

num_teams_per_page = 5


def polling_thread():
    bot.polling()


# Функция для отправки уведомлений о предстоящих матчах
def send_match_notifications():
    pass


@bot.message_handler(commands=['start'])
def start(msg):
    chat_id = msg.chat.id
    keyboard = main_keyboard()

    try:
        add_user_to_db(chat_id)
        bot.send_message(chat_id, START_MAIN_MENU, reply_markup=keyboard)
    except sqlite3.IntegrityError:
        bot.send_message(chat_id, MAIN_MENU, reply_markup=keyboard)
    except Exception as Error:
        log.exception(Error)
        bot.send_message(chat_id, ERROR_MESSAGE)


@bot.message_handler(content_types=["text"])
def all_messages(msg):
    chat_id = msg.chat.id
    message = msg.text
    try:
        user_status = get_user_status(chat_id)

        if message == "⬅️ В главное меню":
            reset_user(chat_id)
            bot.send_message(chat_id, MAIN_MENU, reply_markup=main_keyboard())
        elif message == "Изменить отслеживаемые команды":
            teams = db_teams_get()  # Получаем список команд из базы данных
            set_user_status(chat_id, "page_0")
            markup = gen_markup_teams(chat_id, teams)
            bot.send_message(chat_id, "Выберите команды:", reply_markup=markup)
        elif message == "Матчи":
            set_user_status(chat_id, "matches")
            bot.send_message(chat_id, SELECT_MATCHES, reply_markup=send_matches_keyboard())
        elif message == "Турниры":
            set_user_status(chat_id, "events")
            bot.send_message(chat_id, SELECT_EVENTS, reply_markup=send_events_keyboard())
        elif message == "Активные матчи":
            now_matches = get_live_matches_from_db()
            formatted_live_matches_text = format_live_matches(now_matches)
            if formatted_live_matches_text == '':
                formatted_live_matches_text = 'Нет запланированных матчей'
            bot.send_message(chat_id, formatted_live_matches_text, reply_markup=send_matches_keyboard())
        elif message == "Список интересующих матчей":
            upcoming_matches = get_upcoming_matches_from_db()
            interesting_teams = get_user_selected_teams(chat_id)
            upcoming_matches = [match for match in upcoming_matches if
                                match[0] in interesting_teams or match[1] in interesting_teams]
            formatted_matches_text = format_matches(upcoming_matches)
            if formatted_matches_text == '':
                formatted_matches_text = 'Нет запланированных матчей'
            bot.send_message(chat_id, formatted_matches_text, reply_markup=send_matches_keyboard())
        elif message == "Список всех будущих матчей":
            upcoming_matches = get_upcoming_matches_from_db()
            formatted_matches_text = format_matches(upcoming_matches)
            if formatted_matches_text == '':
                formatted_matches_text = 'Нет запланированных матчей'
            bot.send_message(chat_id, formatted_matches_text, reply_markup=send_matches_keyboard())

    except Exception as Error:
        log.exception(Error)
        bot.send_message(chat_id, ERROR_MESSAGE)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.from_user.id
    if call.data == "next_page":
        page = int(get_user_status(chat_id).split('_')[1])
        set_user_status(chat_id, f'page_{page + 1}')
    elif call.data == "prev_page":
        page = int(get_user_status(chat_id).split('_')[1])
        set_user_status(chat_id, f'page_{page - 1}')
    elif call.data == "end":
        reset_user(chat_id)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выбор записан.")
        return
    else:
        team_name = call.data.split("_")[1]
        selected = call.data.startswith("✅")

        if selected:
            delete_team_from_user(chat_id, team_name)
        else:
            add_team_to_user(chat_id, team_name)

    # Обновляем разметку с кнопками
    teams = db_teams_get()
    markup = gen_markup_teams(chat_id, teams)
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)


# Функция для генерации разметки с кнопками для выбора команд
def gen_markup_teams(chat_id, teams):
    logging.info(get_user_status(chat_id))
    page = int(get_user_status(chat_id).split('_')[1])
    start_index = page * num_teams_per_page
    end_index = min((page + 1) * num_teams_per_page, len(teams))
    teams_to_show = teams[start_index:end_index]

    markup = telebot.types.InlineKeyboardMarkup()

    user_teams = get_user_selected_teams(chat_id)  # Получаем список команд пользователя из базы данных

    for team in teams_to_show:
        team_name = team['name']
        selected = team_name in user_teams  # Проверяем, выбрана ли команда пользователем
        text = f"{'✅' if selected else '❌'} {team_name}"  # Помечаем выбранные команды галочкой
        callback_data = f"{'✅' if selected else '❌'}_{team_name}"
        markup.add(telebot.types.InlineKeyboardButton(text, callback_data=callback_data))

    # row make
    if page != 0 and end_index < len(teams):
        markup.add(telebot.types.InlineKeyboardButton("Prev", callback_data=f"prev_page"),
                   telebot.types.InlineKeyboardButton("Next", callback_data=f"next_page"))
    elif page != 0:
        markup.add(telebot.types.InlineKeyboardButton("Prev", callback_data=f"prev_page"))
    elif end_index < len(teams):
        markup.add(telebot.types.InlineKeyboardButton("Next", callback_data=f"next_page"))
    markup.add(telebot.types.InlineKeyboardButton("Закончить выбор", callback_data=f"end"))
    return markup


create_tables()

# Запускаем бота в отдельном потоке
polling_thread = threading.Thread(target=polling_thread)
polling_thread.start()

while True:
    logging.info("Started to parse")
    db_parse_matches()
    # add_teams_to_db()
    logging.info("Parsed hltv")
    send_match_notifications()
    time.sleep(300)  # Парсинг каждые 5 минут
