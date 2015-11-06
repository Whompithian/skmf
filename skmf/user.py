"""skmf.user by Brendan Sweeney, CSS 593, 2015.

Hold user identifiers and access rights. This class assumes that user data will
be kept in a triplestore alongside other data. User data is considered to be
sensitive and should be safeguarded as such. Passwords should be hashed before
they are passed to the User object, preferably with an algorithm that is meant
for securely hashing passwords. Other fields may have encrypted values passed
to them, so long as the encoding can be read by the attached SPARQL endpoint,
which must be handled outside of this class. id must be a unicode string and it
must be unique for each user. While this class provides a basic schema for a
user, RDF allows for dynamic shaping of its schema by merely adding data, so
this class provides a data element to hold a dictionary of fields that are not
part of the interface of this class.
"""

class User:

    def __init__(self, id = 'admin',
            hashpass =
            b'$2b$12$/t7tQAxpH1cfwIYk.guuIuhQF5GBtoHqaokpxIhsOJNiIng2i.IA.'):
        self.id = id
        self.hashpass = hashpass
        self.name = 'Stewart'
        self.authenticated = False
        self.active = True
        self.data = []

    def get(id):
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
