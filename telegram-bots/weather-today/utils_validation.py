def validate_coordinates(lat, lon):
    try:
        lat = float(lat)
        lon = float(lon)
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            return True
    except Exception:
        pass
    return False

def validate_city(city_name):
    from services_geocoding import geocode_city
    return geocode_city(city_name) is not None

def validate_date(date_str):
    from datetime import datetime
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False 