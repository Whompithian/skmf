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


class Query(object):

    def __init__(self, graphlist = [], labellist = [], subjectlist = {}):
        self.graphs = graphlist
        self.labels = labellist
        self.subjects = subjectlist

    def add_graph(self, graph):
        if graph not in self.graphs:
            self.graphs.append(graph)

    def remove_graph(self, graph):
        while graph in self.graphs:
            self.graphs.remove(graph)

    def add_constraint(self, labellist = [], subjectlist = {}):
        pass

    def remove_constraint(self, labellist = [], subjectlist = {}):
        pass


class Subject(object):

    def __init__(self, id, type = 'uri', graphlist = [], predlist = {}):
        self.id = id
        self.type = type
        self.graphs = graphlist
        self.preds = predlist
        if len(self.preds) == 0:
            results = g.sparql.query_subject(id, type, graphlist)
            self.preds = self.init_values(results)

    def init_values(self, results):
        predlist = {}
        if 'results' in results:
            bindings = results['results']['bindings']
            for binding in bindings:
                predicate = binding['p']['value']
                rdfobject = binding['o']
                type = binding['p']['type']
                value = {'type': type, 'value': [rdfobject]}
                if predicate not in predlist:
                    predlist[predicate] = value
                elif rdfobject not in predlist[predicate]['value']:
                    predlist[predicate]['value'].append(rdfobject)
        return predlist

    def add_graph(self, graph):
        if graph not in self.graphs:
            self.graphs.append(graph)

    def remove_graph(self, graph):
        while graph in self.graphs:
            self.graphs.remove(graph)

    def add_data(self, graphlist = [], predlist = {}):
        new_data = {}
        graphs = []
        for graph in graphlist:
            if graph in self.graphs:
                graphs.append(graph)
        try:
            for predicate in predlist:
                if predicate not in self.preds and len(predlist[predicate]['value']) > 0:
                    self.preds[predicate] = predlist[predicate]
                    new_data[predicate] = predlist[predicate]
                else:
                    type = predlist[predicate]['type']
                    rdfobjects = predlist[predicate]['value']
                    new_data[predicate] = {'type': type, 'value': []}
                    for rdfobject in rdfobjects:
                        if rdfobject not in self.preds[predicate]['value']:
                            self.preds[predicate]['value'].append(rdfobject)
                            new_data[predicate]['value'].append(rdfobject)
                if len(new_data[predicate]['value']) == 0:
                    del new_data[predicate]
            if len(new_data) > 0:
                record = {self.id: {'type': self.type, 'value': new_data}}
                g.sparql.insert(graphs, record)
        except:
            raise

    def remove_data(self, graphlist = [], predlist = {}):
        old_data = {}
        graphs = []
        for graph in graphlist:
            if graph in self.graphs:
                graphs.append(graph)
        for predicate in predlist:
            if predicate in self.preds:
                type = predlist[predicate]['type']
                rdfobjects = predlist[predicate]['value']
                old_data[predicate] = {'type': type, 'value': []}
                for rdfobject in rdfobjects:
                    if rdfobject in self.preds[predicate]['value']:
                        self.preds[predicate]['value'].remove(rdfobject)
                        old_data[predicate]['value'].append(rdfobject)
                if len(self.preds[predicate]['value']) == 0:
                    del self.preds[predicate]
                if len(old_data[predicate]['value']) == 0:
                    del old_data[predicate]
        if len(old_data) > 0:
            record = {self.id: {'type': self.type, 'value': old_data}}
            g.sparql.delete(graphs, record)

    def update_data(self, graphlist = [], predlist = {}):
        g.sparql.update(graphlist, predlist)

    def refresh_store(self):
        g.sparql.drop_subject(self.id, *self.graphs)
        record = {self.id: self.preds}
        g.sparql.insert(*self.graphs, **record)


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
        return self.preds[User.actkey] == 'Y'

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

    def get_hash(self):
        return self.preds[User.hashkey].encode()

    def get_name(self):
        return self.preds[User.namekey]

    def set_hash(self, hashpass):
        value = hashpass.decode('utf-8')
        hashobject = {'value': value, 'type': 'literal'}
        kwargs = {User.hashkey: hashobject}
        success = self.set_values(**kwargs) == 1
        if success:
            self.write()
        return success

    def set_name(self, name):
        nameobject = {'value': name, 'type': 'literal'}
        kwargs = {User.namekey: nameobject}
        success = self.set_values(append=False, **kwargs) == 1
        if success:
            self.write()
        return success

