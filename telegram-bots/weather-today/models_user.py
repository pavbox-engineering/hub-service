class User:
    def __init__(self, user_id, location=None):
        self.user_id = user_id
        self.location = location  # {'lat': ..., 'lon': ...} или None 