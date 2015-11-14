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

from skmf import app, g


class Subject(object):

    def __init__(self, id, *args, **kwargs):
        self.id    = id
        self.graphs = []
        self.data  = {}
        for graph in args:
            self.graphs.append(graph)
        if not kwargs:
            kwargs = g.sparql.query_subject(id, *args)
        self.set_values(**kwargs)

    def get_graph(self):
        return self.graph

    def get_data(self, *args):
        if not args:
            return self.data
        result = {}
        for predicate in args:
            if predicate in self.data:
                result[predicate] = self.data[predicate]
        return result

    def set_graph(self, graph):
        self.graph = graph
        self.write()

    def set_values(self, append = True, **kwargs):
        count = 0
        if kwargs:
            if 'results' in kwargs:
                for result in kwargs['results']['bindings'][0]:
                    predicate = result['p']['value']
                    rdfobject = RDFObject(**result['o'])
                    if predicate not in self.data or not append:
                        self.data[predicate] = [rdfobject]
                        count += 1
                    elif rdfobject not in self.data[predicate]:
                        self.data[predicate].append(rdfobject)
                        count += 1
            else:
                for key, value in kwargs:
                    if not isinstance(value, RDFObject):
                        value = RDFObject(**value)
                    if key not in self.data or not append:
                        self.data[key] = [value]
                        count += 1
                    elif value not in self.data[key]:
                        self.data[key].append(value)
                        count += 1
        return count

    def write(self):
        pass


class User(Subject):

    actkey  = app.config['NAMESPACE'] + 'active'
    hashkey = app.config['NAMESPACE'] + 'hashpass'
    namekey = 'http://xmlns.com/foaf/0.1/name'

    def __init__(self, username, **kwargs):
        #b'$2b$12$/t7tQAxpH1cfwIYk.guuIuhQF5GBtoHqaokpxIhsOJNiIng2i.IA.'
        graph = ['users']
        super(User, self).__init__(id=app.config['NAMESPACE']+username, *graph, **kwargs)
        self.username      = username
        self.authenticated = False

    def get(id):
        user = User(id)
        if User.hashkey in user.data:
            return user
        return None

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return self.data[User.actkey] == 'Y'

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

    def get_hash(self):
        return self.data[User.hashkey].encode()

    def get_name(self):
        return self.data[User.namekey]

    def set_hash(self, hashpass):
        value = hashpass.decode('utf-8')
        hashobject = RDFObject(value=value, type='literal')
        kwargs = {User.hashkey: hashobject}
        success = self.set_values(append=False, **kwargs) == 1
        if success:
            self.write()
        return success

    def set_name(self, name):
        nameobject = RDFObject(value=name, type='literal')
        kwargs = {User.namekey: nameobject}
        success = self.set_values(append=False, **kwargs) == 1
        if success:
            self.write()
        return success


class RDFObject(object):

    def __init__(self, value = None, type = None, datatype = None, xmllang = None, **kwargs):
        self.datatype = None
        self.xmllang  = None
        if value and type:
            self.value = value
            self.type = type
            self.datatype = datatype
            if xmllang:
                self.xmllang = xmllang.lower()
        else:
            try:
                self.value = kwargs['value']
                self.type = kwargs['type']
                if 'datatype' in kwargs:
                    self.datatype = kwargs['datatype']
                if 'xmllang' in kwargs:
                    self.xmllang = kwargs['xmllang'].lower()
            except KeyError:
                return None

    def __eq__(self, other):
        if isinstance(other, RDFObject):
            return self.value == other.value and self.type == other.type and self.datatype == other.datatype and self.xmllang == other.xmllang
        return NotImplemented
