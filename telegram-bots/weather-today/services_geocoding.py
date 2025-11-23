import requests

def geocode_city(city_name):
    url = 'https://nominatim.openstreetmap.org/search'
    params = {
        'q': city_name,
        'format': 'json',
        'limit': 1,
        'addressdetails': 0,
    }
    headers = {'User-Agent': 'WeatherTodayBot/1.0'}
    resp = requests.get(url, params=params, headers=headers, timeout=5)
    if resp.ok and resp.json():
        data = resp.json()[0]
        return {'lat': float(data['lat']), 'lon': float(data['lon'])}
    return None 