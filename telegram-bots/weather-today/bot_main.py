import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from bot_handlers import handle_tomorrow, handle_month, handle_custom_date, handle_location
from utils_validation import validate_date, validate_coordinates, validate_city
from services_weather import get_weather
from services_geocoding import geocode_city
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'PLACEHOLDER_TOKEN')

# Состояния для ConversationHandler
ENTER_DATE, ENTER_LOCATION = range(2)

# Кнопки главного меню
main_keyboard = ReplyKeyboardMarkup([
    ['На завтра', 'На месяц'],
    ['Указать дату'],
    ['Изменить локацию']
], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Привет! Я помогу узнать погоду. Выберите период прогноза:',
        reply_markup=main_keyboard
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Я — бот прогноза погоды. Используйте кнопки для выбора периода или /start для возврата в главное меню.'
    )

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def route_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == 'На завтра':
        await handle_tomorrow(update, context)
    elif text == 'На месяц':
        await handle_month(update, context)
    elif text == 'Указать дату':
        await handle_custom_date(update, context)
        return ENTER_DATE
    elif text == 'Изменить локацию':
        await handle_location(update, context)
        return ENTER_LOCATION
    elif text == 'Назад':
        await start(update, context)
        return ConversationHandler.END
    else:
        await update.message.reply_text('Пожалуйста, выберите действие с помощью кнопок.')

async def process_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date = update.message.text
    if date == 'Назад':
        await start(update, context)
        return ConversationHandler.END
    if not validate_date(date):
        await update.message.reply_text('Некорректный формат даты. Введите в формате ГГГГ-ММ-ДД:')
        return ENTER_DATE
    # Получаем координаты пользователя
    loc = context.user_data.get('location', {'lat': 55.75, 'lon': 37.62})
    weather = get_weather(loc['lat'], loc['lon'], date)
    await update.message.reply_text(f'Погода на {date}: {weather}')
    return ConversationHandler.END

async def process_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    location = update.message.text.strip()
    if location == 'Назад':
        await start(update, context)
        return ConversationHandler.END
    # Проверяем координаты
    if ',' in location:
        parts = location.split(',')
        if len(parts) == 2 and validate_coordinates(parts[0], parts[1]):
            context.user_data['location'] = {'lat': float(parts[0]), 'lon': float(parts[1])}
            await update.message.reply_text('Локация сохранена!')
            return ConversationHandler.END
        else:
            await update.message.reply_text('Некорректные координаты. Введите в формате: широта,долгота')
            return ENTER_LOCATION
    # Проверяем город
    if validate_city(location):
        coords = geocode_city(location)
        context.user_data['location'] = coords
        await update.message.reply_text(f'Локация сохранена: {location}')
        return ConversationHandler.END
    else:
        await update.message.reply_text('Город не найден. Попробуйте ещё раз.')
        return ENTER_LOCATION

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, route_message)],
        states={
            ENTER_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_date)],
            ENTER_LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_location)],
        },
        fallbacks=[CommandHandler('start', start), CommandHandler('menu', menu_command)],
    )
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('menu', menu_command))
    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == '__main__':
    main() 