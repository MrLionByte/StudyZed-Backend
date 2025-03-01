#mimics User Model
class CustomUser:
    def __init__(self, user_data):
        self.id = user_data.get('id')