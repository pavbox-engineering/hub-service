from telegram import ReplyKeyboardMarkup

def main_keyboard():
    return ReplyKeyboardMarkup([
        ['На завтра', 'На месяц'],
        ['Указать дату'],
        ['Изменить локацию']
    ], resize_keyboard=True)

def settings_keyboard():
    return ReplyKeyboardMarkup([
        ['Изменить локацию'],
        ['Назад']
    ], resize_keyboard=True)

def back_keyboard():
    return ReplyKeyboardMarkup([
        ['Назад']
    ], resize_keyboard=True) 