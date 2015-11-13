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

Classes:
Subject -- Representation of all triples that describe a single RDF subject.
User -- Representation of a user of SKMF, made persistent in a SPARQL endpoint.
"""

from skmf import g, app


class Subject:

    def __init__(self, id, graph = '', **kwargs):
        self.id    = id
        self.graph = graph
        self.data  = {}
        self.set_values(False, kwargs)

    def get_graph(self):
        return self.graph

    def get_data(self, *args):
        if not args:
            return self.data
        result = []
        for predicate in args:
            try:
                result.append(self.data[predicate])
            except KeyError:
                pass
        return result

    def set_graph(self, graph):
        self.graph = graph

    def set_values(self, overwrite = False, **kwargs):
        if kwargs:
            try:
                for result in kwargs['results']['bindings'][0]:
                    predicate = result['p']['value']
                    if not self.data[predicate]:
                        self.data[predicate] = []
                    if overwrite:
                        self.data[predicate] = [result['o']]
                    elif result['o'] not in self.data[predicate]:
                        self.data[predicate].append(result['o'])
            except (KeyError, IndexError):
                for key, value in kwargs:
                    if not self.data[key]:
                        self.data[key] = []
                    if overwrite:
                        self.data[key] = [value]
                    elif value not in self.data[key]:
                        self.data[key].append(value)
                self.data = kwargs


class User(Subject):

    actkey  = app.config['NAMESPACE'] + 'active'
    hashkey = app.config['NAMESPACE'] + 'hashpass'
    namekey = 'http://xmlns.com/foaf/0.1/name'

    def __init__(self, id, **kwargs):
        #b'$2b$12$/t7tQAxpH1cfwIYk.guuIuhQF5GBtoHqaokpxIhsOJNiIng2i.IA.'
        super(User, self).__init__(id=id, graph='users', kwargs=kwargs)
        self.authenticated = False

    def get(id):
        result = g.sparql.query_user(id)
        if result:
            user = User(id, result)
            try:
                user.active = '0'
                user.name   = 'value'
                return user
            except (IndexError, KeyError):
                return None
        return None

    def save(self):
        pass

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        actkey = app.config['NAMESPACE'] + 'active'
        return self.data[actkey] == 'Y'

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def get_hash(self):
        return self.data[User.hashkey].encode()

    def get_name(self):
        return self.data[User.namekey]

    def set_hash(self, hashpass):
        return self.data[User.hashkey].encode()

    def set_name(self, name):
        return self.data[User.namekey]
