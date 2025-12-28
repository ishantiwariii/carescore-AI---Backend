from datetime import datetime

class User:
    def __init__(self, uid, email, display_name):
        self.uid = uid
        self.email = email
        self.display_name = display_name
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            "uid": self.uid,
            "email": self.email,
            "display_name": self.display_name,
            "created_at": self.created_at
        }