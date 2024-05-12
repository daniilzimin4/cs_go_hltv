import time
import datetime

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
	conn = sqlite3.connect(DATABASE_PATH)
	cursor = conn.cursor()
	for match in get_upcoming_matches_from_db():
		td = datetime.datetime(*([int(x) for x in match[3].split('-') + match[2].split(':')])) - datetime.datetime.now()
		cursor.execute("SELECT count(*) FROM notifications WHERE" +
		               " teamA=? AND teamB=? AND match_time=? AND date=? AND event=?", match)
		count = cursor.fetchone()[0]
		cursor.execute("SELECT chat_id FROM users_teams WHERE team_name = ? OR team_name = ?", (match[0], match[1]))
		users = cursor.fetchall()
		if td < datetime.timedelta(hours=1) and count == 0 and users:
			for user in set(users):
				bot.send_message(user[0], f"Do not skip\n{match[0]} vs {match[1]}\n" +\
				                 f"Date: {match[3]}, Time: {match[2]}\nEvent: {match[4]}")
			cursor.execute("INSERT INTO notifications VALUES (?, ?, ?, ?, ?)", match)
	conn.commit()
	conn.close()


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

		if message == "⬅️ Main menu":
			reset_user(chat_id)
			bot.send_message(chat_id, MAIN_MENU, reply_markup=main_keyboard())
		elif message == "Monitored teams":
			teams = db_teams_get()  # Получаем список команд из базы данных
			set_user_status(chat_id, "page_0")
			markup = gen_markup_teams(chat_id, teams)
			bot.send_message(chat_id, "Choose teams:", reply_markup=markup)
		elif message == "Matches":
			set_user_status(chat_id, "matches")
			bot.send_message(chat_id, SELECT_MATCHES, reply_markup=send_matches_keyboard())
		elif message == "Ranking":
			teams = db_teams_get()  # Получаем список команд из базы данных
			set_user_status(chat_id, "page_0")
			top = gen_top_teams(chat_id, teams)
			bot.send_message(chat_id, "Ranking:", reply_markup=top)
		elif message == "Live matches":
			now_matches = get_live_matches_from_db()
			formatted_live_matches_text = format_live_matches(now_matches)
			if formatted_live_matches_text == '':
				formatted_live_matches_text = 'No live matches'
			bot.send_message(chat_id, formatted_live_matches_text, reply_markup=send_matches_keyboard())
		elif message == "Matches of monitored teams":
			upcoming_matches = get_upcoming_matches_from_db()
			interesting_teams = get_user_selected_teams(chat_id)
			upcoming_matches = [match for match in upcoming_matches if
			                    match[0] in interesting_teams or match[1] in interesting_teams]
			formatted_matches_text = format_matches(upcoming_matches)
			if formatted_matches_text == '':
				formatted_matches_text = 'No upcoming matches'
			bot.send_message(chat_id, formatted_matches_text, reply_markup=send_matches_keyboard())
		elif message == "All upcoming matches":
			upcoming_matches = get_upcoming_matches_from_db()
			formatted_matches_text = format_matches(upcoming_matches)
			if formatted_matches_text == '':
				formatted_matches_text = 'No upcoming matches'
			bot.send_message(chat_id, formatted_matches_text, reply_markup=send_matches_keyboard())

	except Exception as Error:
		log.exception(Error)
		bot.send_message(chat_id, ERROR_MESSAGE)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
	print(call.data)
	chat_id = call.from_user.id
	type_of_call = 1
	if call.data == "end 1":
		reset_user(chat_id)
		bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Choice saved.")
		return
	elif call.data == "end 2":
		reset_user(chat_id)
		bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
		                      text="Top closed.")
		return
	elif call.data.split()[0] == "next_page":
		page = int(get_user_status(chat_id).split('_')[1])
		set_user_status(chat_id, f'page_{page + 1}')
		type_of_call = int(call.data.split()[1])
	elif call.data.split()[0] == "prev_page":
		page = int(get_user_status(chat_id).split('_')[1])
		set_user_status(chat_id, f'page_{page - 1}')
		type_of_call = int(call.data.split()[1])
	elif call.data.split()[0] == "info":
		team_rank = int(call.data.split()[1])
		info = top30teams()[team_rank]
		players = "\n\t\t"
		for player in get_players(info['team-id']):
			players += player['name'] + f" (id:{player['id']})\n\t\t"

		info_to_show = f"Name: {info['name']}" + \
		               f"\n\t\tRank: {info['rank']}" + \
		               f"\n\t\tTeam id: {info['team-id']}" + \
		               f"\n\t\tRank points: {info['rank-points']}" + \
		               f"\nPlayers: {players}"
		return_button = telebot.types.InlineKeyboardMarkup()
		return_button.add(telebot.types.InlineKeyboardButton("Back", callback_data="prev_page_top"))

		bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
		                      text=info_to_show, reply_markup=return_button)
		return
	elif call.data.split()[0] == "prev_page_top":
		page = int(get_user_status(chat_id).split('_')[1])
		set_user_status(chat_id, f'page_{page}')
		bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Ranking:")
		type_of_call = 2
	else:
		team_name = call.data.split("_")[1]
		selected = call.data.startswith("✅")

		if selected:
			delete_team_from_user(chat_id, team_name)
		else:
			add_team_to_user(chat_id, team_name)

	# Обновляем разметку с кнопками
	if type_of_call == 1:
		teams = db_teams_get()
		markup = gen_markup_teams(chat_id, teams)
		bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
		                              reply_markup=markup)
	else:
		teams = db_teams_get()
		top = gen_top_teams(chat_id, teams)
		bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
		                              reply_markup=top)


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
		markup.add(telebot.types.InlineKeyboardButton("Prev", callback_data="prev_page 1"),
		           telebot.types.InlineKeyboardButton("Next", callback_data="next_page 1"))
	elif page != 0:
		markup.add(telebot.types.InlineKeyboardButton("Prev", callback_data="prev_page 1"))
	elif end_index < len(teams):
		markup.add(telebot.types.InlineKeyboardButton("Next", callback_data="next_page 1"))
	markup.add(telebot.types.InlineKeyboardButton("Close", callback_data="end 1"))
	return markup


def gen_top_teams(chat_id, teams):
	logging.info(get_user_status(chat_id))
	page = int(get_user_status(chat_id).split('_')[1])
	start_index = page * num_teams_per_page
	end_index = min((page + 1) * num_teams_per_page, len(teams))
	teams_to_show = teams[start_index:end_index]

	markup = telebot.types.InlineKeyboardMarkup()

	for team in teams_to_show:
		team_name = team['name']
		text = f"{teams.index(team) + 1}. {team_name}"
		callback_data = f"info {teams.index(team)}"
		markup.add(telebot.types.InlineKeyboardButton(text, callback_data=callback_data))

	# row make
	if page != 0 and end_index < len(teams):
		markup.add(telebot.types.InlineKeyboardButton("Prev", callback_data="prev_page 2"),
		           telebot.types.InlineKeyboardButton("Next", callback_data="next_page 2"))
	elif page != 0:
		markup.add(telebot.types.InlineKeyboardButton("Prev", callback_data="prev_page 2"))
	elif end_index < len(teams):
		markup.add(telebot.types.InlineKeyboardButton("Next", callback_data="next_page 2"))
	markup.add(telebot.types.InlineKeyboardButton("Close", callback_data="end 2"))
	return markup


create_tables()

# Запускаем бота в отдельном потоке
polling_thread = threading.Thread(target=polling_thread)
polling_thread.start()

while True:
	logging.info("Started to parse")
	db_parse_matches()
	add_teams_to_db()
	logging.info("Parsed hltv")
	send_match_notifications()
	time.sleep(300)  # Парсинг каждые 5 минут
