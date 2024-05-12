from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Ranking"))
    keyboard.add(KeyboardButton("Monitored teams"))
    keyboard.add(KeyboardButton("Matches"))
    return keyboard


def send_matches_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Live matches"))
    keyboard.add(KeyboardButton("Matches of monitored teams"))
    keyboard.add(KeyboardButton("All upcoming matches"))
    keyboard.add(KeyboardButton("⬅️ Main menu"))
    return keyboard


def send_events_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Live events"))
    keyboard.add(KeyboardButton("Upcoming events"))
    keyboard.add(KeyboardButton("⬅️ Main menu"))
    return keyboard


def if_caption_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(
        KeyboardButton("✅ Yes"),
        KeyboardButton("❌ No")
    )
    keyboard.add(KeyboardButton("⬅️ Main menu"))

    return keyboard


def back_to_menu_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("⬅️ Main menu"))
    return keyboard
