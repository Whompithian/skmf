"""skmf.sparqler by Brendan Sweeney, CSS 593, 2015.

Perform operations on a SPARQL endpoint, such as inserts, queries, and updates.
Higher-level modules should call this module to interface with the SPARQL end-
point rather than attempting to form and execute their own queries. The SPARQL
endpoint must be available and writable. If it is not, an exception will be
raised, but only once a query is attempted. An attempt is made to keep queries
as generalized as possible so that they may be dynamically formed rather than
using static query strings with variable parameters.

Classes:
    SPARQLER: An extension of SPARQLWrapper to handle special cases for SKMF.
"""

from SPARQLWrapper import JSON, POST, SPARQLWrapper
from SPARQLWrapper.SPARQLExceptions import EndPointInternalError, \
                                           EndPointNotFound, QueryBadFormed

from skmf import app
#import skmf.i18n.en_US as uiLabel


class SPARQLER(SPARQLWrapper):
    """Extend SPARQLWrapper to handle special cases for the SKMF package.
    
    Most of the behavior and functionality of SPARQLWrapper are maintained. The new query and update methods try to be as generic and dynamic as possible to allow for the creation of queries from an unknown set of conditions. Many SPARQL features, such as functions, may never be implemented.
    """

    def __init__(self, endpoint, updateEndpoint=None,
                 returnFormat=JSON, defaultGraph=None):
        """Create a SPARQLWrapper object, ensuring the JSON return format.
        
        Args:
            defaultGraph (str): URI of the default graph for all operations.
            endpoint (str): URL, port, and path of the SPARQL query endpoint.
            returnFormat (str): Should be JSON for SKMF.
            updateEndpoint (str): URL, port, and path of the update endpoint.
        """
        super(SPARQLER, self).__init__(endpoint=endpoint,
                                       updateEndpoint=updateEndpoint,
                                       returnFormat=returnFormat,
                                       defaultGraph=defaultGraph)

    def _set_graphs(self, graphlist = set()):
        """Return a string for the full 'FROM' section of a SPARQL query.
        
        The empty string denotes the default graph. Otherwise, the named graph URI is formed by combining the local namespace with the name of the graph, separated by '/'. Depending on the SPARQL endpoint, omitting the graph may have the same effect as providing only the default graph.
        
        Args:
            graphlist (set): Named graphs to include in the 'FROM' section.
        
        Returns:
            String of FROM lines for a SPARQL query.
        """
        namespace = app.config['NAMESPACE']
        graphs = []
        for graph in graphlist:
            if graph == '':
                graphuri = namespace
            else:
                graphuri = '{}/{}'.format(namespace, graph)
            graphs.append('FROM <{}>'.format(graphuri))
        return '\n        '.join(graphs)

    def _set_labels(self, labellist = set()):
        """Return the header string for a SPARQL query.
        
        If no labels are provided, the wildcard '*' is assumed. Leading white space is used as a separator to avoid trailing white space at the end of the line.
        
        Args:
            labellist (list): Header labels for query placeholders.
        
        Returns:
            String of header labels for a SPARQL query.
        """
        if not labellist:
            labels = '*'
        else:
            labels = []
            for label in labellist:
                labels.append('?{}'.format(label))
        return ' '.join(labels)

    def _format_body(self, subjectlist = {}):
        """Format text for the body of a SPARQL query from the given subjects.
        
        Most of the work is done by a nested method. At this level, a period is placed at the end of each line and a newline is added to all but the last body line.
        
        Args:
            subjectlist (dict): Triples that form the content of a query.
        
        Returns:
            String containing the body for a SPARQL query.
        """
        body = []
        for subject in subjectlist:
            sentence = self._format_subject(subject, subjectlist[subject])
            # period marks the end of a single subject match
            body.append('{} .'.format(sentence))
        return '\n          '.join(body)

    def _format_subject(self, subject, predlist = {}):
        """Format all text for one subject of a SPARQL query.
        
        The subject may be represented as an URI, a label, or a prefixed name. A prefixed name does not require any formatting, but it does depend on the presence of the corresponding prefix in the final query string. The predicate list must contain the 'type' key to indicate which formatting option is used. The 'value' key should point to the actual data to pass to the next formatter.
        
        Args:
            predlist (dict): Predicates and objects associated with a subject.
            subject (str): URI, label, or prefixed name of one RDF subject.
        
        Returns:
            String of a complete statement in the body of a SPARQL query.
        """
        body = []
        padding = ' ;\n            '
#        try:
        for predicate in predlist['value']:
            clause = self._format_predicate(predicate,
                                            predlist['value'][predicate])
            body.append(clause)
#        except KeyError:
#            raise QueryBadFormed(uiLabel.errorSpqrqlQuerySubject)
        if predlist['type'] == 'uri':
            return '<{}> {}'.format(subject, padding.join(body))
        elif predlist['type'] == 'label':
            return '?{} {}'.format(subject, padding.join(body))
        return '{} {}'.format(subject, padding.join(body))

    def _format_predicate(self, predicate, objectlist = {}):
        """Format all text for one predicate of a SPARQL query.
        
        The predicate may be represented as an URI, a label, or a prefixed name. A prefixed name does not require any formatting, but it does depend on the presence of the corresponding prefix in the final query string. The object list must contain the 'type' key to indicate which formatting option is used. The 'value' key should point to the actual data to pass to the next formatter.
        
        Args:
            objectlist (dict): Objects associated with a subject and predicate.
            predicate (str): URI, label, or prefixed name of a predicate.
        
        Returns:
            String of a SPARQL statement from just after the subject.
        """
        body = []
        padding = ' ,\n              '
#        try:
        rdfobjects = objectlist['value']
        for rdfobject in rdfobjects:
            word = self._format_object(rdfobject)
            body.append(word)
#        except KeyError:
#            raise QueryBadFormed(uiLabel.errorSparqlQueryPred)
        if objectlist['type'] == 'uri':
            return '<{}> {}'.format(predicate, padding.join(body))
        elif objectlist['type'] == 'label':
            return '?{} {}'.format(predicate, padding.join(body))
        return '{} {}'.format(predicate, padding.join(body))

    def _format_object(self, rdfobject = {}):
        """Format the text for one RDF object of a SPARQL query.
        
        The object may be represented as an URI, a label, or a prefixed name. A prefixed name does not require any formatting, but it does depend on the presence of the corresponding prefix in the final query string. The object must contain the 'type' key to indicate which formatting option is used. The 'value' key should point to the actual data to pass to the next formatter. An optional 'xml:lang' key may be present for type = 'literal' to indicate text language.
        
        Args:
            rdfobject (dict): Object associated with a subject and predicate.
        
        Returns:
            String of a SPARQL statement from just after one predicate.
        """
#        try:
        if rdfobject['type'] == 'uri':
            body = ['<{}>'.format(rdfobject['value'])]
        elif rdfobject['type'] == 'label':
            body = ['?{}'.format(rdfobject['value'])]
        elif rdfobject['type'] == 'literal':
            body = ['"{}"'.format(rdfobject['value'])]
            if 'xml:lang' in rdfobject:
                body.append('@{}'.format(rdfobject['xml:lang'].lower()))
            elif 'datatype' in rdfobject:
                body.append('^^{}'.format(rdfobject['datatype']))
        else:
            body = ['{}'.format(rdfobject['value'])]
#        except KeyError:
#            raise QueryBadFormed(uiLabel.errorSparqlQueryObject)
        return ''.join(body)

    def _format_optional(self, optlist = []):
        """Format a query body section prefixed with the keyword 'OPTIONAL'.
        
        The use of 'OPTIONAL' allows extra information to be pulled from a query without restricting which items are returned by the main body of the query. The primary motivation of this method is to allow the rdfs:label to always be returned with any object that is returned by the query.
        
        Returns:
            String of a SPARQL OPTIONAL statement.
        """
        optionals = []
        for optional in optlist:
            body = self._format_body(optional)
            optionals.append('OPTIONAL {{ {body} }}'.format(body=body))
        return '\n          '.join(optionals)

    def query_general(self, graphlist = {''}, labellist = set(), subjectlist = {}, optlist = []):
        """Return the results of an arbitrarily complex SELECT query.
        
        A boilerplate is provided for a SELECT query. The formatting is performed by helper methods, one for each of the main sections. EVENTUALLY, this method will be generalized enough to allow most SPARQL query types.
        
        Args:
            graphlist (set): Named graphs in which to scope the query.
            labellist (set): Header labels for the query results.
            subjectlist (dict): Structured data that define the query.
        
        Returns:
            JSON object containing SPARQL query results.
        
        Raises:
            
        """
        prefix = app.config['PREFIXES']
        graphs = self._set_graphs(graphlist)
        labels = self._set_labels(labellist)
        body = self._format_body(subjectlist)
        optional = self._format_optional(optlist)
        queryString = """
        {prefix}
        SELECT DISTINCT {labels}
        {graphs}
        WHERE {{
          {body}
          {optional}
        }}
        """.format(prefix=prefix, labels=labels, graphs=graphs, body=body, optional=optional)
        self.setQuery(queryString)
        print(queryString)
#        try:
        return self.queryAndConvert()
#        except EndPointNotFound:
#            raise
#        except QueryBadFormed:
#            raise
#        except EndPointInternalError:
#            raise

    def query_subject(self, id, type = 'uri', graphlist = {''}):
        """Return all predicates and objects of the subject having id.
        
        Primarily used to initialize a Subject from the 'resource' module. The components of a query are assembled to return all predicates and objects associated with the identified subject. It is not considered an error if the object does not exist.
        
        Args:
            graphlist (set): Named graphs in which to scope the query.
            id (str): URI or prefixed name to identify the query subject.
            type (str): Should be 'uri' or 'pfx' for prefixed name.
        
        Returns:
            Result of SPARQL query for predicates and objects of a subject.
        """
        rdfobject = {'type': 'label', 'value': 'o'}
        predicate = {'p': {'type': 'label', 'value': [rdfobject]}}
        subject = {id: {'type': type, 'value': predicate}}
        labels = {'p', 'o'}
        return self.query_general(graphlist, labels, subject)

    def _update(self, action, graphlist = set(), subjectlist = {}):
        """Perform update actions against a SPARQL endpoint.
        
        A boilerplate is provided for an UPDATE statement. The formatting is performed by helper methods, one for each of the main sections. EVENTUALLY, this method will be generalized enough to allow most SPARQL update actions.
        
        Args:
            action (str): The update action, either 'INSERT' or 'DELETE'.
            graphlist (set): Named graphs in which to perform the update.
            subjectlist (dict): Structured data that define the update.
        
        Raises:
            
        """
        prefix = app.config['PREFIXES']
        namespace = app.config['NAMESPACE']
        graphs = graphlist
        body = self._format_body(subjectlist)
        for graph in graphs:
            if not graph:
                graph = namespace
            else:
                graph = '{}/{}'.format(namespace, graph)
            queryString = """
            {prefix}
            {action} DATA {{
              GRAPH <{graph}> {{
                {body}
              }}
            }}
            """.format(prefix=prefix, action=action, graph=graph, body=body)
            print(queryString)
            self.setQuery(queryString)
            self.setMethod(POST)
            try:
                self.query()
            except (EndPointNotFound, QueryBadFormed, EndPointInternalError):
                raise

    def insert(self, graphlist = set(), subjectlist = {}):
        """Perform an INSERT of some RDF triples into a triplestore.
        
        Args:
            graphlist (set): Named graphs in which to perform the insertion.
            subjectlist (dict): Structured data to be placed in a triplestore.
        """
        self._update(action='INSERT', graphlist=graphlist,
                     subjectlist=subjectlist)

    def delete(self, graphlist = set(), subjectlist = {}):
        """Perform a DELETE of some RDF triples from a triplestore.
        
        Args:
            graphlist (set): Named graphs in which to perform the deletion.
            subjectlist (dict): Structured data to be removed from triplestore.
        """
        self._update(action='DELETE', graphlist=graphlist, 
                    subjectlist=subjectlist)
