from telegram import Update
from telegram.ext import ContextTypes
from services_weather import get_weather
from bot_keyboards import back_keyboard

async def handle_tomorrow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    loc = context.user_data.get('location', {'lat': 55.75, 'lon': 37.62})
    from datetime import datetime, timedelta
    tomorrow = (datetime.now().date() + timedelta(days=1)).isoformat()
    weather = get_weather(loc['lat'], loc['lon'], tomorrow)
    await update.message.reply_text(f'Погода на завтра: {weather}')

async def handle_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    loc = context.user_data.get('location', {'lat': 55.75, 'lon': 37.62})
    # Open-Meteo максимум 16 дней
    weather = get_weather(loc['lat'], loc['lon'], None, days=16)
    await update.message.reply_text(f'Погода на 16 дней:\n{weather}')

async def handle_custom_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Введите дату в формате ГГГГ-ММ-ДД:', reply_markup=back_keyboard())

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Введите город или координаты:', reply_markup=back_keyboard()) 