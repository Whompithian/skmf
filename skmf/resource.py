"""skmf.resource by Brendan Sweeney, CSS 593, 2015.

This module holds classes that model RDF triples and SPARQL queries. The structure of the primary data element of most classes is a dict modeled after the JSON response format for SPARQL, but with reduced redundancy inspired by the Turtle format for RDF serialization. The structure allows for valid triples and query elements with placeholders to coexist and exchange components. Most of these components are directly passable to the 'sparqler' module. ACCESS controls will be implemented using graphs as ACLs, but this is proving tricky.

Classes:
Query -- Representation of a free-form SPARQL query or update request.
Subject -- Representation of all triples that describe a single RDF subject.
User -- Representation of a user of SKMF, made persistent in a SPARQL endpoint.
"""

from skmf import app, g


class Query(object):
    """Components of a free-form SPARQL query or update request.
    
    A Query holds the relationships between resources that are to be queried from a SPARQL endpoint. A list of graphs may optionally be stored to broaden the scope of the query beyond the datastore's default graph. For the query to have meaning beyond verifying that a set of triples exists in the datastore (there are other types of query for this), a list of labels should be stored to represent the header of the query results. Each label should coincide with a <subject_label>, a <predicate_label>, or an <object_label> that appears in the 'subjects' attribute. This attribute holds a dict that describes the structure of a SPARQL query. The keyword is either the URI of the subject, if known, or a placeholder label. The value is another dict whose 'type' key specifies whether the parent keyword is a URI or label. The 'value' key points to another dict whose keywords are predicate URIs and labels. The corresponding value is a dict with a 'type' key that specifies whether the parent keyword is a URI or a label and whose 'value' key specifies a list of RDF objects as formatted for JSON. In the RDF object, 'xml:lang' is optional and 'datatype' may be provided, but it will be ignored. The 'type' and 'value' keys are required at all three levels.
    
    Attributes:
        graphs (optional[list]): Graphs in which to scope queries SPARQL.
        labels (list): Header labels expected to be returned from a query.
        subjects (dict): Triples, with placeholders, to describe the query. The
            format should be:
            {<subject_uri>|<subject_label>:
                {'type': 'uri'|'label',
                 'value':
                    {<predicate_uri>|<predicate_label>:
                        {'type': 'uri'|'label',
                         'value':
                            [{'type': 'uri'|'label'|'literal',
                              'value': <ojbect_uri>|<object_label>|<literal>,
                              'xml:lang': <lang_string>
                            }]
                        }
                    }
                }
            }
    """

    def __init__(self, graphlist = [''], labellist = [], subjectlist = {}):
        """Setup the lists and dictionary to hold the query elements.
        
        A Query may be set with empty values and still be valid. If no graphs are provided, the backend is expected to scope the query to the triplestore's default graph, represented by an empty string. If no labels are provided, the backend is expected to scope the query to 'SELECT *', which relies on the labels provided in the subject list. In any case, if no subjects are provided, any query should be expected to return an empty result set.
        
        Args:
            graphlist (list): Additional graphs to which to scope a query.
            labellist (list): Labels for the header of query results.
            subjectlist (dict): Description of query element relationships.
        """
        self.graphs = graphlist
        self.labels = labellist
        self.subjects = subjectlist

    def add_graphs(self, graphlist):
        """Append one or more named graphs to be included in any queries.
        
        If a graph in the provided list already exists in the local graph list, then it is ignored.
        
        Args:
            graphlist (list): New named graphs to include in future queries.
        """
        for graph in graphlist:
            if graph not in self.graphs:
                self.graphs.append(graph)

    def remove_graphs(self, graphlist):
        """Remove one or more named graphs from inclusion in future queries.
        
        If a graph in the provided list is not present in the local graph list, then it is ignored.
        
        Args:
            graphlist (list): Named graphs to exclude from future queries.
        """
        for graph in graphlist:
            while graph in self.graphs:
                self.graphs.remove(graph)

    def add_constraints(self, subject = None, type = None,
                       labellist = [], subjectlist = {}):
        """Add placeholder and relationship constraints to refine a query.
        
        New constraints may be provided as a combination of a Subject class object and a dict of subjects as stored by the Query class. The former requires the presence of the 'type' argument and requires more parsing than the latter. Typically, entries in the label list will coincide with the Subject id - if provided and if type = 'label' - or with a <subject_label>, a <predicate_label>, or an <object_label> that appears in the subject list, though this need not be the case. Labels may be provided on their own, for instance, if one was previously omitted by mistake. Only the smallest non-matching component of each argument is added. Any element of an argument that already exists in this Query is silently ignored.
        
        Args:
            labellist (list): Labels for the header of query results.
            subject (Subject): Subject that contains triples to refine a query.
            subjectlist(dict): Description of query element relationships.
            type (str): The type of Subject id string, either 'uri' or 'label'.
        """
        pass

    def remove_constraints(self, subject = None,
                          labellist = [], subjectlist = {}):
        """Remove placeholder and relationship constraints from a query.
        
        Unlike with addition, removal does not require a type to be specified for a Subject, since the 'subjects' dict guarantees the uniqueness of its id. Only the smallest matching component of each argument is added. Any element of an argument that does not already exist in this Query is silently ignored.
        
        Args:
            labellist (list): Labels for the header of query results.
            subject (Subject): Subject that contains triples to refine a query.
            subjectlist(dict): Description of query element relationships.
        """
        pass


class Subject(object):
    """JSON/TTL-like serialization of a subject described in RDF.
    
    An instance of a Subject typically encompasses all of the predicates and associated RDF objects that describe one RDF subject in a triplestore. It may also store just a subset of that information or the elements of a query that pertain to a single subject, either by URI or through a placeholder label. The 'type' attribute is used to specify which and the 'id' attribute holds the actual URI or label string. A list of graphs may also be maintained to specify which graphs are part of any query that is performed on the Subject.
    
    Attributes:
        id (str): URI or label that identifies this Subject in a query.
        graphs (list): Graphs in which to scope queries for this Subject.
        preds (dict): Predicates and objects that describe this Subject. The format should match that of the second inner dict in Query, with the predicate id as the key:
            {<predicate_uri>|<predicate_label>:
                {'type': 'uri'|'label',
                 'value':
                    [{'type': 'uri'|'label'|'literal',
                      'value': <ojbect_uri>|<object_label>|<literal>,
                      'xml:lang': <lang_string>
                    }]
                }
            }
        type (str): How to interpret the id, one of 'uri', 'label', or 'NONE'.
    """

    def __init__(self, id, type = 'uri', graphlist = [], predlist = {}):
        """Setup using defaults, provided values, or from the triplestore.
        
        If no predicate list is provided and 'type' is set to 'uri' - the default - then it is assumed that this Subject should be retrieved from the provided list of graphs based on the 'id' argument. This assumption is made to prevent the formation of a Subject that already exists in the triplestore but is treated as a new RDF subject. The only way to override this behavior is to set 'type' to something other than 'uri', although it is not recommended to use 'label' since that already has another meaning.
        
        Args:
            graphlist (list): Named graphs to which a subject may belong.
            id (str): Unique value to assign to this subject for queries.
            predlist (dict): Predicates and their associated objects.
            type (str): 'uri' for SPARQL URI or 'label' for a placeholder.
        """
        self.id = id
        self.type = type
        self.graphs = ['']
        self.graphs.extend(graphlist)
        self.preds = predlist
        if self.type == 'uri' and not self.preds:
            results = g.sparql.query_subject(id, type, graphlist)
            self.preds = self._init_values(results)

    def _init_values(self, results):
        """Returns all triples about this subject from a triplestore.
        
        The input is expected to follow the JSON syntax for SPARQL query responses. Moreover, it is exptected to contain 'p' and 'o' labels, representing the predicates and objects, respectively, that make up RDF triples that contain this Subject as their subject. If the wrong information is passed in, then an invalid Subject may be formed.
        
        Args:
            results (dict): JSON format results of SPARQL query for a subject.
        Returns:
            A graph containing descriptive predicates and associated objects.
        """
        predlist = {}
        if 'results' in results:
            try:
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
            except KeyError:
                pass
        return predlist

    def add_graphs(self, graphlist):
        """Append new graphs to the list of graphs to query for this subject.
        
        If a graph in the provided list is not present in the local graph list, then it is ignored.
        
        Params:
            graphlist (list): Short names of named graphs in the triplestore.
        """
        for graph in graphlist:
            if graph not in self.graphs:
                self.graphs.append(graph)

    def remove_graphs(self, graphlist):
        """Remove a graph from the list of graphs to query for this subject.
        
        If a graph in the provided list is not present in the local graph list, then it is ignored.
        
        Params:
            str:graph -- Short name of a named graph in the triplestore.
        """
        for graph in graphlist:
            while graph in self.graphs:
                self.graphs.remove(graph)

    def add_data(self, graphlist = [], predlist = {}):
        """Add new triples that describe this subject to the triplestore.
        
        The provided graph list is used to determine to which graphs triples are added, but any graphs that are not attributed to this Subject are ignored to support access control mechanisms.
        
        Params:
            graphlist (list): Named graphs that should hold the new triples.
            predlist (list): New data to add, in the same format at self.preds.
        Returns:
            The list of graphs that were available for adding triples.
            The dictionary of predicates that were actually added.
        Raises:
            
        """
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
                if not new_data[predicate]['value']:
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
        
        The provided graph list is used to determine from which graphs triples are deleted, but any graphs that are not attributed to this Subject are ignored to support access control mechanisms.
        
        Params:
            graphlist (list): Named graphs from which to delete triples.
            predlist (graph): Data to delete, in the same format as self.preds.
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
                    if not self.preds[predicate]['value']:
                        del self.preds[predicate]
                    if not old_data[predicate]['value']:
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
    """Wrapper around a subject for use in front-ends with user sessions.
    
    Hold user identifiers and access rights. This class assumes that user data will be kept in a triplestore alongside other data. User data should be considered sensitive. Passwords should be hashed before they are passed to the User object, preferably with an algorithm that is meant for generating secure password hashes. Other fields may have encrypted values passed to them, so long as the encoding of those values can be read by the attached SPARQL endpoint. id must be a unicode string and it must be unique for each user. Since this system does not allow users to authenticate anonymously, a User must have a hashpass value.
    
    Attributes:
        actkey (str): URL of the 'active' predicate for a user's active state.
        authenticated (bool): State of authentication for login sessions.
        hashkey (str): URL of the 'hashpass' predicate for hashed passwords.
        namekey (str): URL of the 'name' predicate for user display name.
        username (str): Name portion of the Subject id.
    """

    actkey  = app.config['NAMESPACE'] + 'active'
    hashkey = app.config['NAMESPACE'] + 'hashpass'
    namekey = 'http://xmlns.com/foaf/0.1/name'

    def __init__(self, username, predlist = {}):
        """Create a Subject and set a username and authentication status.
        
        Once the underlying Subject is initialized, the username is stored and 'authenticated' is set to 'False' do denote that the user exists but has not yet provided credentials. The login handler is expected to set this attribute to 'True' upon successful authentication by the user.
        
        Agrs:
            predlist (dict): New User information, same format as self.preds.
            username (str): Unique user id, same as name portion of Subject id.
        """
        #b'$2b$12$/t7tQAxpH1cfwIYk.guuIuhQF5GBtoHqaokpxIhsOJNiIng2i.IA.'
        namespace = app.config['NAMESPACE']
        id = namespace + username
        graph = ['users']
        super(User, self).__init__(id=id, graphlist=graph, predlist=predlist)
        self.username      = username
        self.authenticated = False

    def get(username):
        """Return a User, if found, from the triplestore from their username.
        
        Users must have the 'active' and 'hashpass' predicates associated with them in the triplestore to be valid. If the SPARQL query results do not include these two parameters, then they are ignored. It is up to the caller to determine how to handle an inactive User.
        
        Args:
            username (str): Unique user id, same as name portion of Subject id.
        Returns:
            A User if username was found in the triplestore, otherwise 'None'.
        """
        user = User(username)
        if User.hashkey in user.preds and User.actkey in user.preds:
            return user
        return None

    def is_authenticated(self):
        """Return 'True' if the user is authenticated, 'False' otherwise."""
        return self.authenticated

    def is_active(self):
        """Return 'True' if the user is active, 'False' otherwise."""
        return self.preds[User.actkey] == 'Y'

    def is_anonymous(self):
        """Return 'False' - not used, but needed for Flask-Login."""
        return False

    def get_id(self):
        """Return the unique username of a user."""
        return self.username

    def get_hash(self):
        """Return byte-string of a user's password hash."""
        return self.preds[User.hashkey].encode()

    def get_name(self):
        """Return the display name of a user."""
        return self.preds[User.namekey]

    def set_hash(self, hashpass):
        """Replace the existing password hash with a new one.
        
        THIS method is currently very risky. It works by removing the original password hash, then creating a new one. It is possible that it may be interrupted after the first operation, leaving a user unable to authenticate. Until proper UPDATEs are implemented, this action should be avoided.
        
        Args:
            hashpass (bytestring): Auth token for use in future authentication.
        """
        newvalue = hashpass.decode('utf-8')
        newobject = {'value': newvalue, 'type': 'literal'}
        newpred = {User.hashkey: {'type': 'uri', 'value': [newobject]}}
        graphlist = ['users']
        dropvalue = {}
        if User.hashkey in self.preds:
            dropvalue[User.hashkey] = self.preds[User.hashkey]
            self.remove_data(graphlist, dropvalue)
        self.add_data(graphlist, newpred)

    def set_name(self, name):
        """Replace the exisitng display name with a new one."""
        nameobject = {'value': name, 'type': 'literal'}
        kwargs = {User.namekey: nameobject}
        success = self.set_values(append=False, **kwargs) == 1
        if success:
            self.write()
        return success
