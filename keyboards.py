from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Топ команд"))
    keyboard.add(KeyboardButton("Отслеживаемые команды"))
    keyboard.add(KeyboardButton("Матчи"))
    return keyboard


def send_matches_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Live матчи"))
    keyboard.add(KeyboardButton("Список интересующих матчей"))
    keyboard.add(KeyboardButton("Список всех будущих матчей"))
    keyboard.add(KeyboardButton("⬅️ В главное меню"))
    return keyboard


def send_events_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Активные турниры"))
    keyboard.add(KeyboardButton("Будущие турниры"))
    keyboard.add(KeyboardButton("⬅️ В главное меню"))
    return keyboard


def if_caption_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(
        KeyboardButton("✅ Да"),
        KeyboardButton("❌ Нет")
    )
    keyboard.add(KeyboardButton("⬅️ В главное меню"))

    return keyboard


def back_to_menu_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("⬅️ В главное меню"))
    return keyboard
