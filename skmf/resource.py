"""skmf.resource by Brendan Sweeney, CSS 593, 2015.

This module holds classes that model RDF triples and SPARQL queries. The
structure of the primary data element of most classes is a dict modeled after
the JSON response format for SPARQL, but with reduced redundancy inspired by
the Turtle format for RDF serialization. The structure allows for valid triples
and query elements with placeholders to coexist and exchange components. Most
of these components are directly passable to the 'sparqler' module. ACCESS
CONTROLS will be implemented using graphs as ACLs, but this is proving tricky.

Classes:
    Query: Representation of a free-form SPARQL query or update request.
    Subject: Representation of all triples that describe a single RDF subject.
    User: Representation of SKMF user, made persistent in a SPARQL endpoint.
"""

from skmf import app, g


class Query(object):
    """Components of a free-form SPARQL query or update request.
    
    A Query holds the relationships between resources that are to be queried
    from a SPARQL endpoint. A list of graphs may optionally be stored to
    broaden the scope of the query beyond the datastore's default graph. For
    the query to have meaning beyond verifying that a set of triples exists in
    the datastore (there are other types of query for this), a list of labels
    should be stored to represent the header of the query results. Each label
    should coincide with a <subject_label>, a <predicate_label>, or an
    <object_label> that appears in the 'subjects' attribute. This attribute
    holds a dict that describes the structure of a SPARQL query. The keyword is
    either the URI or appropriate prefixed name of the subject, if known, or a
    placeholder label. The value is another dict whose 'type' key specifies
    whether the parent keyword is a URI or label. The 'value' key points to
    another dict whose keywords are predicate URIs, prefixes, and labels. The
    corresponding value is a dict with a 'type' key that specifies whether the
    parent keyword is a URI or a label and whose 'value' key specifies a list
    of RDF objects as formatted for JSON. In the RDF object, 'xml:lang' is
    optional and 'datatype' may be provided, but is seldom needed. The 'type'
    and 'value' keys are required at all three levels.
    
    Attributes:
        graphs (optional[list]): Graphs in which to scope queries SPARQL.
        labels (list): Header labels expected to be returned from a query.
        optionals (list): Triples that are optional to a SPARQL query.
        subjects (dict): Triples, with placeholders, to describe the query. The
            format should be:
            {<subject_uri>|<subject_label>:
                {'type': 'uri'|'pfx'|'label',
                 'value':
                    {<predicate_uri>|<predicate_label>:
                        {'type': 'uri'|'pfx'|'label',
                         'value':
                            [{'type': 'uri'|'pfx'|'label'|'literal',
                              'value': <ojbect_uri>|<object_label>|<literal>,
                              'xml:lang': <lang_string>
                              'datatype': <xml_datatype>
                            }]
                        }
                    }
                }
            }
    """

    def __init__(self, graphlist = {''}, labellist = set(),
                 subjectlist = {}, optlist = []):
        """Setup the local lists and dictionary to hold the query elements.
        
        A Query may be set with empty values and still be valid. If no graphs
        are provided, the backend is expected to scope the query to the triple-
        store's default graph, represented by an empty string. If no labels are
        provided, the backend is expected to scope the query to 'SELECT *',
        which relies on the labels provided in the subject list. In any case,
        if no subjects are provided, any query should be expected to return an
        empty result set.
        
        Args:
            graphlist (set): Additional graphs to which to scope a query.
            labellist (set): Labels for the header of query results.
            optlist (list): dicts representing optional sub-statements.
            subjectlist (dict): Description of query element relationships.
        """
        self.graphs = graphlist
        self.labels = labellist
        self.subjects = subjectlist
        self.optionals = optlist

    def _add_preds(self, subject, predlist):
        """Add some predicates to the specified subject of this Query.
        
        Each predicate is added only if at least one of the RDF objects it
        holds can be added. The provided predicate list is checked for consist-
        ency, but it is assumed that the local subject list is already well-
        formed and contains the subject in the argument list. To prevent
        KeyError from being raised while adding objects, an empty string is
        paired with the 'value' key in a dict that is paired with the predicate
        in a stored subject. If the list does not get populated, then this dict
        is removed. Any predicates that are successfully added are appended to
        a dict that is returned upon completion.
        
        Args:
            predlist (dict): Predicates and objects to add to this Query.
            subject (str): ID of the subject to which the predicates apply.
        
        Returns:
            dict of predicates and RDF objects that were successfully added.
        """
        new_preds = {}
        for pred in predlist:
            if predlist[pred]['value'] and predlist[pred]['type']:
                new_type = predlist[pred]['type']
                if pred not in self.subjects[subject]['value']:
                    # to prevent KeyError at lower levels
                    empty = {}
                    empty['type'] = new_type
                    empty['value'] = []
                    self.subjects[subject]['value'][pred] = empty
                objectlist = predlist[pred]['value']
                new_objects = self._add_objects(subject, pred, objectlist)
                if new_objects:
                    new_value = {}
                    new_value['type'] = new_value
                    new_value['value'] = new_objects
                    new_preds[pred] = new_value
                # cleanup if no objects were added
                if not self.subjects[subject]['value'][pred]['value']:
                    del self.subjects[subject]['value'][pred]
        return new_preds

    def _add_objects(self, subj, pred, objectlist):
        """Add objects to the specified subject and predicate of this Query.
        
        Each object is added only if it does not already exist in the 'value' component of the specified predicate within the specified subject. The provided object list is checked for consistency, but it is assumed that the local subject list is already well-formed and contains the subject in the argument list, along with the corresponding predicate. Any RDF objects that are successfully added are appended to a list that is returned upon completion.
        
        Args:
            objectlist (list): RDF objects to apply to a subject and predicate.
            pred (str): ID of the predicate to which the RDF objects apply.
            subj (str): ID of the subject to which the RDF objects apply.
        
        Returns:
            list of valid RDF objects that were successfully added.
        """
        new_objects = []
        for object in objectlist:
            if object['type'] and object['value']:
                if object not in self.subjects[subj]['value'][pred]['value']:
                    self.subjects[subj]['value'][pred]['value'].append(object)
                    new_objects.append(object)
        return new_objects

    def _remove_preds(self, subject, predlist):
        """Remove some predicates from the specified subject of this Query.
        
        Each predicate is removed only if all of the RDF objects it held were
        also removed. The provided predicate list is checked for consistency,
        but it is assumed that the local subject list is already well-formed
        and contains the subject in the argument list. Any predicates that had
        at least one object removed, however, are appended, along with those
        objects, to a dict that is returned upon completion.
        
        Args:
            predlist (dict): Predicates and objects to remove from this Query.
            subject (str): ID of the subject to which the predicates apply.
        
        Returns:
            dict of predicates and RDF objects that were successfully removed.
        """
        old_preds = {}
        for pred in predlist:
            if pred in self.subjects[subject]['value']:
                if predlist[pred]['value'] and predlist[pred]['type']:
                    objectlist = predlist[pred]['value']
                    objects = self._remove_objects(subject, pred, objectlist)
                    if objects:
                        old_type = predlist[pred]['type']
                        old_value = {}
                        old_value['type'] = old_type
                        old_value['value'] = objects
                        old_preds[pred] = old_value
                        if not self.subjects[subject]['value'][pred]['value']:
                            del self.subjects[subject]['value'][pred]
        return old_preds

    def _remove_objects(self, subj, pred, objectlist):
        """Remove some predicates from the specified subject of this Query.
        
        Each object is removed only if it already exists in the 'value'
        component of the specified predicate within the specified subject. The
        provided object list is checked for consistency, but it is assumed that
        the local subject list is already well-formed and contains the subject
        in the argument list, along with the corresponding predicate. Any RDF
        objects that are successfully removed are appended to a list that is
        returned upon completion.
        
        Args:
            objectlist (list): Objects to remove from a subject and predicate.
            pred (str): ID of the predicate to which the RDF objects apply.
            subj (str): ID of the subject to which the RDF objects apply.
        
        Returns:
            list of RDF objects that were successfully removed.
        """
        old_objects = []
        for object in objectlist:
            if object in self.subjects[subj]['value'][pred]['value']:
                self.subjects[subj]['value'][pred]['value'].remove(object)
                old_objects.append(object)
        return old_objects

    def _set_label_constraints(self):
        """Ensure the rdfs:label, if available, is returned with each result.
        
        The label list is effectively doubled to ensure a location to store the
        rdfs:label of each named placeholder in the query that has rdfs:label 
        set. This increases the readability of query results for the user.
        """
        label_labels = set()
        for label in self.labels:
            if '_label' not in label:
                label_label = '{}_label'.format(label)
                label_object = {}
                label_object['type'] = 'label'
                label_object['value'] = label_label
                pred_value = {}
                pred_value['type'] = 'pfx'
                pred_value['value'] = [label_object]
                label_pred = {'rdfs:label': pred_value}
                subject_value = {}
                subject_value['type'] = 'label'
                subject_value['value'] = label_pred
                label_subject = {label: subject_value}
                label_labels.add(label_label)
                self.optionals.append(label_subject)
        self.labels.update(label_labels)

    def add_graphs(self, graphlist):
        """Append one or more named graphs to be included in any queries.
        
        If a graph in the provided list already exists in the local graph list,
        then it is ignored.
        
        Args:
            graphlist (set): New named graphs to include in future queries.
        """
        self.graphs.update(graphlist)

    def remove_graphs(self, graphlist):
        """Remove one or more named graphs from inclusion in future queries.
        
        If a graph in the provided list is not present in the local graph list,
        then it is ignored.
        
        Args:
            graphlist (set): Named graphs to exclude from future queries.
        """
        self.graphs.difference_update(graphlist)

    def add_constraints(self, subject = None, type = None,
                       labellist = set(), subjectlist = {}):
        """Add placeholders and relationship constraints to refine a query.
        
        New constraints may be provided as a combination of a Subject class
        object and a dict of subjects as stored by the Query class. The former
        requires the presence of the 'type' argument. Typically, entries in the
        label list will coincide with the Subject id - if provided and if
        type = 'label' - or with a <subject_label>, a <predicate_label>, or an
        <object_label> that appears in the subject list, though this need not
        be the case. Labels may be provided on their own, for instance, if one
        was previously omitted by mistake. Only the smallest non-matching
        component of each argument is added. Any element of an argument that
        already exists in this Query is silently ignored.
        
        Args:
            labellist (set): Labels for the header of query results.
            subject (Subject): Subject that contains triples to refine a query.
            subjectlist(dict): Description of query element relationships.
            type (str): The type of Subject id string, either 'uri' or 'label'.
        
        Returns:
            A list and dict of the components that were successfully added.
        """
        new_subjects = {}
        new_labels = labellist.difference(self.labels)
        self.labels.update(new_labels)
        if subject and type:
            if subject.preds:
                if subject.id not in self.subjects:
                    # to prevent KeyError at lower levels
                    empty = {}
                    empty['type'] = type
                    empty['value'] = {}
                    self.subjects[subject.id] = empty
                new_preds = self._add_preds(subject.id, subject.preds)
                if new_preds:
                    new_value = {}
                    new_value['type'] = type
                    new_value['value'] = new_preds
                    new_subjects[subject.id] = new_value
                # cleanup if no predicates were added
                if not self.subjects[subject.id]['value']:
                    del self.subjects[subject.id]
        for subj in subjectlist:
            if subjectlist[subj]['value'] and subjectlist[subj]['type']:
                new_type = subjectlist[subj]['type']
                if subj not in self.subjects:
                    # to prevent KeyError at lower levels
                    empty = {}
                    empty['type'] = new_type
                    empty['value'] = {}
                    self.subjects[subj] = empty
                predlist = subjectlist[subj]['value']
                new_preds = self._add_preds(subj, predlist)
                if new_preds:
                    new_value = {}
                    new_value['type'] = new_type
                    new_value['value'] = new_preds
                    new_subjects[subj] = new_value
                # cleanup if no predicates were added
                if not self.subjects[subj]['value']:
                    del self.subjects[subj]
        return new_labels, new_subjects

    def remove_constraints(self, subject = None,
                          labellist = set(), subjectlist = {}):
        """Remove placeholder and relationship constraints from a query.
        
        Unlike with addition, removal does not require a type to be specified
        for a Subject, since the 'subjects' dict guarantees the uniqueness of
        its id. Only the smallest matching component of each argument is
        removed. Any element of an argument that does not already exist in this
        Query is silently ignored.
        
        Args:
            labellist (set): Labels for the header of query results.
            subject (Subject): Subject that contains triples to refine a query.
            subjectlist(dict): Description of query element relationships.
        
        Returns:
            A list and dict of the components that were successfully removed.
        """
        old_subjects = {}
        old_labels = self.labels.intersection(labellist)
        self.labels.difference_update(old_labels)
        if subject:
            if subject.id in self.subjects:
                old_value = self._remove_preds(subject, subject.preds)
                if old_value:
                    old_subjects[subject.id] = old_value
                    if not self.subjects[subject.id]['value']:
                        del self.subjects[subject.id]
        for subj in subjectlist:
            if subj in self.subjects:
                if subjectlist[subj]['value']:
                    old_preds = subjectlist[subj]['value']
                    old_value = self._remove_preds(subj, old_preds)
                    if old_value:
                        old_subjects[subj] = old_value
                        if not self.subjects[subj]['value']:
                            del self.subjects[subj]
        return old_labels, old_subjects

    def submit_query(self):
        """Query a SPARQL endpoint based on stored parameters.
        
        A general query is performed to request data from the SPARQL endpoint
        as described by the the 'labels' and 'subjects' attributes. Every named
        graph in the 'graphs' attribute is included in the query. If no
        exception is raised, then a JSON object containing the query results is
        returned.
        
        Returns:
            Unpacked JSON object containing the SPARQL query results, or None.
        """
        return g.sparql.query_general(graphlist=self.graphs,
                                      labellist=self.labels,
                                      subjectlist=self.subjects,
                                      optlist=self.optionals)

    def submit_insert(self):
        """Insert stored parameters in a SPARQL endpoint.
        
        An INSERT is performed on a SPARQL endpoint of triples as described by
        the 'subjects' attribute. INSERT DATA ignores labels, since it does not
        have a WHERE clause.
        
        Returns:
            True if there were no SPARQLER errors, False otherwise.
        """
        return g.sparql.insert(graphlist=self.graphs,
                               subjectlist=self.subjects)

    def submit_delete(self):
        """Delete stored parameters from a SPARQL endpoint.
        
        A DELETE is performed on a SPARQL endpoint of triples as described by
        the 'subjects' attribute. DELETE DATA ignores labels, since it does not
        have a WHERE clause.
        
        Returns:
            True if there were no SPARQLER errors, False otherwise.
        """
        return g.sparql.delete(graphlist=self.graphs,
                               subjectlist=self.subjects)

    def get_resources(self, category):
        """Retrieve every instance of the specified category of resource.
        
        Resources are the main components handled by the user interface. These
        are used to scope and refine queries for page and form layouts to
        prevent the user from being overwhelmed with too many selections at
        once.
        
        Args:
            category (str): Prefix form of a predicate for which to query.
        
        Returns:
            List of subjects that have the supplied predicate applied to them.
        """
        label_list = {'resource', 'label'}
        resource_object = {}
        resource_object['type'] = 'pfx'
        resource_object['value'] = category
        label_object = {}
        label_object['type'] = 'label'
        label_object['value'] = 'label'
#        comment_object = {}
#        comment_object['type'] = 'label'
#        comment_object['value'] = 'comment'
        pred_value = {}
        pred_value['type'] = 'pfx'
        pred_value['value'] = [resource_object]
        predicates = {'a': pred_value}
        label_value = {}
        label_value['type'] = 'pfx'
        label_value['value'] = [label_object]
        opt_preds = {'rdfs:label': label_value}
#        comment_value = {}
#        comment_value['type'] = 'pfx'
#        comment_value['value'] = [comment_object]
#        predicates['rdfs:comment'] = comment_value
        sub_value = {}
        sub_value['type'] = 'label'
        sub_value['value'] = predicates
        subject = {'resource': sub_value}
        opt_sub_value = {}
        opt_sub_value['type'] = 'label'
        opt_sub_value['value'] = opt_preds
        opt_subject = {'resource': opt_sub_value}
        result = g.sparql.query_general(graphlist=self.graphs,
                                        labellist=label_list,
                                        subjectlist=subject,
                                        optlist=[opt_subject])
        if result:
            return result['results']['bindings']
        return None

    def get_entries(self, entrylist = []):
        """Retrieve the results of a query that was assembled by a user.
        
        The UI is expected to present the query body to the user as the
        opportunity to provide a set of triples. Those triples are then formed,
        one-by-one, into subjects that can be applied to the Query's 'subjects'
        store. Each entry must be checked for type so that the list of labels
        can be maintained. Before running the query, _set_label_constraints()
        is called to ensure that rdfs:label tags will be returned whenever they
        are available.
        
        Args:
            entrylist (list): RDF triples that combine to form a SPARQL query.
        
        Returns:
            List of results of a general query requested by the user.
        """
        label_list = set()
        for entry in entrylist:
            object_type = entry['object']['type']
            object_value = entry['object']['value']
            if not object_value:
                break
            if object_type == 'label':
                label_list.add(object_value)
            rdfobject = {}
            rdfobject['type'] = object_type
            rdfobject['value'] = object_value
            pred_type = entry['predicate']['type']
            pred_value = entry['predicate']['value']
            if not pred_value:
                break
            if pred_type == 'label':
                label_list.add(pred_value)
            rdf_pred = {}
            rdf_pred['type'] = pred_type
            rdf_pred['value'] = [rdfobject]
            predicate = {pred_value: rdf_pred}
            subject_type = entry['subject']['type']
            subject_value = entry['subject']['value']
            if not subject_value:
                break
            if subject_type == 'label':
                label_list.add(subject_value)
            rdf_subject = {}
            rdf_subject['type'] = subject_type
            rdf_subject['value'] = predicate
            subject = {subject_value: rdf_subject}
            self.add_constraints(subjectlist=subject)
        self.add_constraints(labellist=label_list)
        self._set_label_constraints()
        return self.submit_query()['results']['bindings']

    def add_resource(self, category, label, desc, lang = ''):
        """INSERT entries with one skmf:Resource as the subject.
        
        Resources are assumed to have certain attributes to give them a
        consistent view in the user interface. They must specify a category to
        distinguish if they are to be treated primarily as subjects
        (skmf:Resource) or predicates (rdf:Property). They must have rdfs:label
        and rdfs:comment defined to make them understandable to human users.
        They may optionally specify the language for string literals as an ISO
        language code.
        
        Args:
            category (str): One of skmf:Resource, rdf:property.
            desc (str): Detailed description of the new resource.
            label (str): Readable name from which the id is derived.
            lang (str): ISO language code to associate with 'label' and 'desc'.
        """
        new_id = ''.join(c for c in label if c.isalnum()).rstrip().lower()
        id_uri = '{}#{}'.format(app.config['NAMESPACE'], new_id)
        subject = Subject(id_uri, type='uri')
        if not subject.preds:
            cat_objects = []
            cat_object = {}
            cat_object['type'] = 'pfx'
            cat_object['value'] = category
            cat_objects.append(cat_object)
            if category == 'skmf:Resource':
                new_object = {}
                new_object['type'] = 'pfx'
                new_object['value'] = 'rdfs:Class'
                cat_objects.append(new_object)
            label_object = {}
            label_object['type'] = 'literal'
            label_object['value'] = label
            desc_object = {}
            desc_object['type'] = 'literal'
            desc_object['value'] = desc
            if lang:
                label_object['xml:lang'] = lang
                desc_object['xml:lang'] = lang
            pred_value = {}
            pred_value['type'] = 'pfx'
            pred_value['value'] = cat_objects
            new_preds = {'a': pred_value}
            label_value = {}
            label_value['type'] = 'pfx'
            label_value['value'] = [label_object]
            new_preds['rdfs:label'] = label_value
            desc_value = {}
            desc_value['type'] = 'pfx'
            desc_value['value'] = [desc_object]
            new_preds['rdfs:comment'] = desc_value
            return subject.add_data(graphlist={''}, predlist=new_preds)


class Subject(object):
    """JSON/TTL-like serialization of a subject described in RDF.
    
    An instance of a Subject typically encompasses all of the predicates and
    associated RDF objects that describe one RDF subject in a triplestore. It
    may also store just a subset of that information or the elements of a query
    that pertain to a single subject, either by URI or through a placeholder
    label. The 'type' attribute is used to specify which and the 'id' attribute
    holds the actual URI or label string. A list of graphs may also be
    maintained to specify which graphs are part of any query that is performed
    on the Subject.
    
    Attributes:
        id (str): URI or label that identifies this Subject in a query.
        graphs (list): Graphs in which to scope queries for this Subject.
        preds (dict): Predicates and objects that describe this Subject. The
            format should match that of the second inner dict in Query, with
            the predicate id as the key:
            {<predicate_uri>|<predicate_label>:
                {'type': 'uri'|'pfx'|'label',
                 'value':
                    [{'type': 'uri'|'pfx'|'label'|'literal',
                      'value': <ojbect_uri>|<object_label>|<literal>,
                      'xml:lang': <lang_string>
                    }]
                }
            }
        type (str): How to interpret the id, one of 'uri', 'pfx', or 'label'.
    """

    def __init__(self, id, type = 'uri', graphlist = set(), predlist = {}):
        """Setup using defaults, provided values, or from the triplestore.
        
        If no predicate list is provided and 'type' is set to 'uri' - the
        default - then it is assumed that this Subject should be retrieved from
        the provided list of graphs based on the 'id' argument. This assumption
        is made to prevent the formation of a Subject that already exists in
        the triplestore but is treated as a new RDF subject. The only way to
        override this behavior is to set 'type' to something other than 'uri',
        although it is not recommended to use 'label' since that already has
        another meaning.
        
        Args:
            graphlist (set): Named graphs to which a subject may belong.
            id (str): Unique value to assign to this subject for queries.
            predlist (dict): Predicates and their associated objects.
            type (str): 'uri' for SPARQL URI or 'label' for a placeholder.
        """
        self.id = id
        self.type = type
        self.graphs = {''}
        self.graphs.update(graphlist)
        self.preds = predlist
        if self.type != 'label' and not self.preds:
            results = g.sparql.query_subject(id, type, graphlist)
            self.preds = self._init_values(results)

    def _init_values(self, results):
        """Returns all triples about this subject retrieved from a triplestore.
        
        The input is expected to follow the JSON syntax for SPARQL query
        responses. Moreover, it is exptected to contain 'p' and 'o' labels,
        representing the predicates and objects, respectively, that make up RDF
        triples that contain this Subject as their subject. If the wrong
        information is passed in, then an invalid Subject may be formed.
        
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
            except KeyError as e:
                print(__name__, str(e))
                return None
        return predlist

    def add_graphs(self, graphlist):
        """Append new graphs to the list of graphs to query for this subject.
        
        If a graph in the provided list is not present in the local graph list,
        then it is ignored.
        
        Args:
            graphlist (set): Short names of named graphs in the triplestore.
        """
        self.graphs.update(graphlist)

    def remove_graphs(self, graphlist):
        """Remove a graph from the list of graphs to query for this subject.
        
        If a graph in the provided list is not present in the local graph list,
        then it is ignored.
        
        Args:
            graphlist (set): Short names of named graphs in the triplestore.
        """
        self.graphs.difference_update(graphlist)

    def add_data(self, graphlist, predlist = {}):
        """Add new triples that describe this subject to the triplestore.
        
        The provided graph list is used to determine to which graphs triples
        are added, but any graphs that are not attributed to this Subject are
        ignored in order to support access control mechanisms. No default graph
        is provided for INSERTs, so this list must not be empty.
        
        Params:
            graphlist (set): Named graphs that should hold the new triples.
            predlist (dict): New data to add, in the same format at self.preds.
        
        Returns:
            The list of graphs that were available for adding triples.
            The dictionary of predicates that were actually added.
        """
        new_preds = {}
        new_graphs = self.graphs.intersection(graphlist)
        for predicate in predlist:
            if predlist[predicate]['value'] and predlist[predicate]['type']:
                new_type = predlist[predicate]['type']
                rdfobjects = predlist[predicate]['value']
                temp = {}
                temp['type'] = new_type
                temp['value'] = []
                # to avoid KeyError during iteration
                if predicate not in self.preds:
                    self.preds[predicate] = temp
                for rdfobject in rdfobjects:
                    if rdfobject['value'] and rdfobject['type']:
                        if rdfobject not in self.preds[predicate]['value']:
                            self.preds[predicate]['value'].append(rdfobject)
                            assert temp['value']
                if temp['value']:
                    new_preds[predicate] = temp
                else:
                    del self.preds[predicate]
        if new_preds:
            rec_value = {}
            rec_value['type'] = self.type
            rec_value['value'] = new_preds
            record = {self.id: rec_value}
            g.sparql.insert(new_graphs, record)
        return new_graphs, new_preds

    def remove_data(self, graphlist, predlist = {}):
        """Delete triples for this subject from some graphs in the triplestore.
        
        The provided graph list is used to determine from which graphs triples
        are deleted, but any graphs that are not attributed to this Subject are
        ignored in order to support access control mechanisms. No default graph
        is provided for DELETEs, so this list must not be empty.
        
        Params:
            graphlist (set): Named graphs from which to delete triples.
            predlist (graph): Data to delete, in the same format as self.preds.
        
        Returns:
            The list of graphs that were available for removing triples.
            The dictionary of predicates that were actually deleted.
        """
        old_preds = {}
        old_graphs = self.graphs.intersection(graphlist)
        for predicate in predlist:
            if predlist[predicate]['value'] and predlist[predicate]['type']:
                if predicate in self.preds:
                    old_type = predlist[predicate]['type']
                    rdfobjects = predlist[predicate]['value']
                    temp = {'type': old_type, 'value': []}
                    for rdfobject in rdfobjects:
                        if rdfobject in self.preds[predicate]['value']:
                            self.preds[predicate]['value'].remove(rdfobject)
                            temp['value'].append(rdfobject)
                    if temp['value']:
                        old_preds[predicate] = temp
                        if not self.preds[predicate]['value']:
                            del self.preds[predicate]
        if old_preds:
            rec_value = {}
            rec_value['type'] = self.type
            rec_value['value'] = old_preds
            record = {self.id: rec_value}
            g.sparql.delete(old_graphs, record)
        return old_graphs, old_preds

    def update_data(self, graphlist = [], predlist = {}):
        """NOT IMPLEMENTED: Perform conditional UPDATEs"""
        g.sparql.update(graphlist, predlist)

    def refresh_store(self):
        """NOT IMPLEMENTED: Write when the cache is stale"""
        pass


class User(Subject):
    """Wrapper around a subject for use in front-ends with user sessions.
    
    Hold user identifiers and access rights. This class assumes that user data
    will be kept in a triplestore alongside other data. User data should be
    considered sensitive. Passwords should be hashed before they are passed to
    the User object, preferably with an algorithm that is meant for generating
    secure password hashes. Other fields may have encrypted values passed to
    them, so long as the encoding of those values can be read by the attached
    SPARQL endpoint. 'id' must be a unicode string and it must be unique for
    each user. Since this system does not allow users to authenticate
    anonymously, a User must have a 'hashpass' value.
    
    Attributes:
        actkey (str): URL of the 'active' predicate for a user's active state.
        authenticated (bool): State of authentication for login sessions.
        hashkey (str): URL of the 'hashpass' predicate for hashed passwords.
        namekey (str): URL of the 'name' predicate for user display name.
        username (str): Name portion of the Subject 'id'.
    """

    actkey  = '{}#active'.format(app.config['NAMESPACE'])
    hashkey = '{}#hashpass'.format(app.config['NAMESPACE'])
    namekey = 'http://xmlns.com/foaf/0.1/name'

    def __init__(self, username, predlist = {}):
        """Create a Subject and set a username and authentication status.
        
        Once the underlying Subject is initialized, the username is stored and
        'authenticated' is set to 'False' do denote that the user exists but
        has not yet provided credentials. The login handler is expected to set
        this attribute to 'True' upon successful authentication by the user.
        
        Agrs:
            predlist (dict): New User information, same format as self.preds.
            username (str): Unique user id, same as name portion of Subject id.
        """
        id = 'skmf:{}'.format(username)
        graph = {'users'}
        super().__init__(id=id, type='pfx', graphlist=graph, predlist=predlist)
        self.username = username
        self.authenticated = False

    def get(username):
        """Return a User, if found, from the triplestore from their username.
        
        Users must have the 'active' and 'hashpass' predicates associated with
        them in the triplestore to be valid. If the SPARQL query results do not
        include these two parameters, then they are ignored. It is up to the
        caller to determine how to handle an inactive User.
        
        Args:
            username (str): Unique user id, same as name portion of Subject id.
        
        Returns:
            A User if username was found in the triplestore, otherwise 'None'.
        """
        user = User(username)
        if User.actkey in user.preds and User.hashkey in user.preds:
            return user
        return None

    def is_authenticated(self):
        """Return 'True' if the user is authenticated, 'False' otherwise."""
        return self.authenticated

    def is_active(self):
        """Return 'True' if the user is active, 'False' otherwise."""
        active = False
        act_object = self.preds[User.actkey]['value'][0]
        if act_object:
            active = act_object['value'] != '0'
        return active

    def is_anonymous(self):
        """Return 'False' - not used, but needed for Flask-Login."""
        return False

    def get_id(self):
        """Return the unique username of a user."""
        return self.username

    def get_hash(self):
        """Return byte-string of a user's password hash."""
        hash_object = self.preds[User.hashkey]['value'][0]
        return hash_object['value'].encode()

    def get_name(self):
        """Return the display name of a user."""
        if User.namekey in self.preds:
            name_object = self.preds[User.namekey]['value'][0]
            return name_object['value']
        return self.get_id()

    def set_active(self):
        """Set the state of a user to active. No way to undo ATM."""
        if User.actkey not in self.preds:
            new_object = {}
            new_object['type'] = 'literal'
            new_object['value'] = '1'
            pred_value = {}
            pred_value['type'] = 'uri'
            pred_value['value'] = [new_object]
            new_pred = {User.actkey: pred_value}
            graphlist = {'users'}
            self.add_data(graphlist, new_pred)

    def set_hash(self, hashpass):
        """Replace the existing password hash with a new one.
        
        THIS method is currently very risky. It works by removing the original
        password hash, then creating a new one. It is possible that it may be
        interrupted after the first operation, leaving a user unable to
        authenticate. Until proper UPDATEs are implemented, this action should
        be avoided.
        
        Args:
            hashpass (bytestring): Auth token for use in future authentication.
        """
        new_value = hashpass.decode('utf-8')
        new_object = {}
        new_object['type'] = 'literal'
        new_object['value'] = new_value
        pred_value = {}
        pred_value['type'] = 'uri'
        pred_value['value'] = [new_object]
        new_pred = {User.hashkey: pred_value}
        graphlist = {'users'}
        drop_value = {}
        if User.hashkey in self.preds:
            drop_value[User.hashkey] = self.preds[User.hashkey]
            self.remove_data(graphlist, drop_value)
        self.add_data(graphlist, new_pred)

    def set_name(self, name):
        """NOT IMPLEMENTED: Replace exisitng display name with new one."""
        nameobject = {}
        nameobject['type'] = 'literal'
        nameobject['value'] = name
        kwargs = {User.namekey: nameobject}
        success = self.set_values(append=False, **kwargs) == 1
        if success:
            self.write()
        return success
