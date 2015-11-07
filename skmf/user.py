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
part of the interface of this class. Since this system does not allow users
to authenticate anonymously, a User must have a hashpass value.
"""

from skmf import g


class User:

    def __init__(self, id, hashpass, name = '', active = True):
#            b'$2b$12$/t7tQAxpH1cfwIYk.guuIuhQF5GBtoHqaokpxIhsOJNiIng2i.IA.'
        self.id            = id
        self.hashpass      = hashpass
        self.name          = name
        self.authenticated = False
        self.active        = active

    def get(id):
        result = g.sparql.query_user(id)
        if result:
            try:
                data        = result['results']['bindings'][0]
                user        = User(id, data['hashpass']['value'].encode())
                user.active = data['active']['value'] != '0'
                user.name   = data['name']['value']
                return user
            except IndexError:
                return None
            except KeyError:
                return None
        return None

    def save(self):
        pass

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id
