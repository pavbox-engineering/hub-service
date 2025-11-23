import requests
from datetime import datetime, timedelta

def get_weather(lat, lon, date=None, days=1):
    base_url = 'https://api.open-meteo.com/v1/forecast'
    params = {
        'latitude': lat,
        'longitude': lon,
        'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode',
        'timezone': 'auto',
    }
    if date:
        params['start_date'] = params['end_date'] = date
    elif days > 1:
        today = datetime.now().date()
        params['start_date'] = today.isoformat()
        params['end_date'] = (today + timedelta(days=days-1)).isoformat()
    try:
        resp = requests.get(base_url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if 'daily' not in data or not data['daily']['time']:
            return 'Нет данных о погоде.'
        if date or days == 1:
            t_max = data['daily']['temperature_2m_max'][0]
            t_min = data['daily']['temperature_2m_min'][0]
            precip = data['daily']['precipitation_sum'][0]
            wcode = data['daily']['weathercode'][0]
            desc = weather_code_to_text(wcode)
            return f"{desc}. Температура: {t_min}…{t_max}°C, осадки: {precip} мм"
        else:
            # Форматируем прогноз на несколько дней
            lines = []
            for i, day in enumerate(data['daily']['time']):
                t_max = data['daily']['temperature_2m_max'][i]
                t_min = data['daily']['temperature_2m_min'][i]
                precip = data['daily']['precipitation_sum'][i]
                wcode = data['daily']['weathercode'][i]
                desc = weather_code_to_text(wcode)
                lines.append(f"{day}: {desc}, {t_min}…{t_max}°C, осадки: {precip} мм")
            return '\n'.join(lines)
    except Exception as e:
        return f'Ошибка получения погоды: {e}'

def weather_code_to_text(code):
    # WMO weather codes (основные)
    mapping = {
        0: 'Ясно',
        1: 'Преимущественно ясно',
        2: 'Переменная облачность',
        3: 'Пасмурно',
        45: 'Туман',
        48: 'Туман с изморозью',
        51: 'Морось слабая',
        53: 'Морось умеренная',
        55: 'Морось сильная',
        61: 'Дождь слабый',
        63: 'Дождь умеренный',
        65: 'Дождь сильный',
        71: 'Снег слабый',
        73: 'Снег умеренный',
        75: 'Снег сильный',
        80: 'Ливень слабый',
        81: 'Ливень умеренный',
        82: 'Ливень сильный',
        95: 'Гроза',
        96: 'Гроза с градом',
        99: 'Гроза с сильным градом',
    }
    return mapping.get(code, 'Погода неизвестна') 