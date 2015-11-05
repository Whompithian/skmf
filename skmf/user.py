"""skmf.user by Brendan Sweeney, CSS 593, 2015.

Hold user identifiers and access rights.
"""

class User:

    def __init__(self, id = 'admin'):
        self.id = id
        self.hashpass = b'$2b$12$/t7tQAxpH1cfwIYk.guuIuhQF5GBtoHqaokpxIhsOJNiIng2i.IA.'
        self.authenticated = True
        self.active = True

    def get(self, id):
        if id == 'admin':
            return User(id)
        return None

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id
