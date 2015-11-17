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
Query -- Representation of a free-form SPARQL query or update request.
Subject -- Representation of all triples that describe a single RDF subject.
User -- Representation of a user of SKMF, made persistent in a SPARQL endpoint.
"""

from skmf import app, g


class Query(object):
    """Components of a free-form SPARQL query or update request.
    
    Methods:
        add_constraint -- Refine a query with placeholders and relationships.
        add_graph -- Append a graph to include in queries.
        remove_constraint -- Remove query placeholders and relationships.
        remove_graph -- Remove a graph from inclusion in queries.
    """

    def __init__(self, graphlist = [], labellist = [], subjectlist = {}):
        """Setup the lists and dictionary to hold the query elements."""
        self.graphs = graphlist
        self.labels = labellist
        self.subjects = subjectlist

    def add_graph(self, graph):
        """Append a named graph to include in any queries."""
        if graph not in self.graphs:
            self.graphs.append(graph)

    def remove_graph(self, graph):
        """Remove a named graph from inclusion in any queries."""
        while graph in self.graphs:
            self.graphs.remove(graph)

    def add_constraint(self, labellist = [], subjectlist = {}):
        """Add placeholder and relationship constraints to refine a query."""
        pass

    def remove_constraint(self, labellist = [], subjectlist = {}):
        """Remove placeholders and relationship constraints from a query."""
        pass


class Subject(object):
    """JSON/TTL-like serialization of a subject described in RDF.
    
    Methods:
        add_data -- Add triples to the triplestore using this subject.
        add_graph -- Append to the list of graphs to query.
        init_values -- Get all triples about this subject from a triplestore.
        remove_data -- Delete triples for this subject from a triplestore.
        remove_graph -- Remove from the list of graphs to query.
        update_data -- Placeholder: should be moved to Query.
        refresh_store -- Placeholder: probably not needed.
    """

    def __init__(self, id, type = 'uri', graphlist = [], predlist = {}):
        """Setup using defaults, provided values, or from the triplestore.
        
        Params:
            str: id -- Unique value to identify this subject in a triplestore.
            str: type -- 'uri' for known values or 'label' for a placeholder.
            graphlist -- List of named graphs to which a subject belongs.
            predlist -- Descriptive predicates and their associated objects.
        """
        self.id = id
        self.type = type
        self.graphs = graphlist
        self.preds = predlist
        if len(self.preds) == 0:
            # no information provided, check if it exists in the triplestore
            results = g.sparql.query_subject(id, type, graphlist)
            self.preds = self.init_values(results)

    def init_values(self, results):
        """Returns all triples about this subject from a triplestore.
        
        Params:
            results: JSON formatted results of a SPARQL query for one subject.
        Returns:
            A graph containing descriptive predicates and associated objects.
        """
        predlist = {}
        if 'results' in results:
            # expect SPARQL query results in JSON format
            bindings = results['results']['bindings']
            for binding in bindings:
                predicate = binding['p']['value']
                rdfobject = binding['o']
                type = binding['p']['type']
                value = {'type': type, 'value': [rdfobject]}
                if predicate not in predlist:
                    # no collision, safe to add an initial set
                    predlist[predicate] = value
                elif rdfobject not in predlist[predicate]['value']:
                    predlist[predicate]['value'].append(rdfobject)
        return predlist

    def add_graph(self, graph):
        """Append a graph to the list of graphs to query for this subject.
        
        Params:
            str: graph -- Short name of a named graph in the triplestore.
        """
        if graph not in self.graphs:
            self.graphs.append(graph)

    def remove_graph(self, graph):
        """Remove a graph from the list of graphs to query for this subject.
        
        Params:
            str: graph -- Short name of a named graph in the triplestore.
        """
        while graph in self.graphs:
            self.graphs.remove(graph)

    def add_data(self, graphlist = [], predlist = {}):
        """Add new triples that descript this subject to the triplestore.
        
        Params:
            graphlist -- List of named graphs that should hold the new triples.
            predlist -- The new data to add, in the same format at self.preds.
        Returns:
            The list of graphs that were available for adding triples.
            The dictionary of predicates that were actually added.
        Raises:
            
        """
        #: placeholder for predicates that provide new descriptions
        new_data = {}
        #: placeholder for valid named graphs
        graphs = []
        for graph in graphlist:
            # user should use add_graph if any would be skipped
            if graph in self.graphs:
                graphs.append(graph)
        try:
            for predicate in predlist:
                if predicate not in self.preds and len(predlist[predicate]['value']) > 0:
                    # only add new triples to avoid polluting the triplestore
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
                return graphs, record
        except:
            return None
        return graphs

    def remove_data(self, graphlist = [], predlist = {}):
        """Delete triples for this subject from some graphs in the triplestore.
        
        Params:
            graphlist -- List of named graphs from which to delete triples.
            predlist -- The data to delete, in the same format at self.preds.
        Returns:
            The list of graphs that were available for removing triples.
            The dictionary of predicates that were actually deleted.
        Raises:
            
        """
        old_data = {}
        graphs = []
        for graph in graphlist:
            if graph in self.graphs:
                graphs.append(graph)
        try:
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
                return graphs, record
        except:
            return None
        return graphs

    def update_data(self, graphlist = [], predlist = {}):
        """"""
        g.sparql.update(graphlist, predlist)

    def refresh_store(self):
        g.sparql.drop_subject(self.id, *self.graphs)
        record = {self.id: self.preds}
        g.sparql.insert(*self.graphs, **record)


class User(Subject):
    """Wrapper around a subject for use in front-ends with user sessions."""

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
