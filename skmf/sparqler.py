"""skmf.sparqler by Brendan Sweeney, CSS 593, 2015.

Perform operations on a SPARQL endpoint, such as inserts, queries, and updates.
Higher-level modules should call this module to interface with the SPARQL end-
point rather than attempting to form and execute their own queries. The SPARQL
endpoint must be available and writable. If it is not, an exception will be
raised, but only once a query is attempted. An attempt is made to keep queries
as generalized as possible so that they may be dynamically formed rather than
using static query strings with variable parameters.

Classes:
SPARQLER -- An extension of SPARQLWrapper to handle special cases for SKMF.
"""

from SPARQLWrapper import JSON, POST, SPARQLWrapper
from SPARQLWrapper.SPARQLExceptions import EndPointInternalError, \
                                           EndPointNotFound, QueryBadFormed

from skmf import app
import skmf.i18n.en_US as uiLabel

class SPARQLER(SPARQLWrapper):
    """Extend SPARQLWrapper to handle special cases for the SKMF package.
    
    Most of the behavior and functionality of SPARQLWrapper are maintained. A
    few methods are added to handle boilerplate queries with some dynamic
    elements.
    
    Methods:
        Make these queries really pop!
    """

    def __init__(self, endpoint, updateEndpoint=None,
                 returnFormat=JSON, defaultGraph=None):
        super(SPARQLER, self).__init__(endpoint,
                                       updateEndpoint=updateEndpoint,
                                       returnFormat=returnFormat,
                                       defaultGraph=defaultGraph)

    def _set_graphs(self, graphlist = []):
        graphs = 'FROM <{namespace}>'.format(namespace=app.config['NAMESPACE'])
        for graph in graphlist:
            graph = app.config['NAMESPACE'] + '/' + graph
            graphs += '\nFROM <{graph}>'.format(graph=graph)
        return graphs

    def _set_labels(self, labellist = []):
        if len(labellist) == 0:
            labels = ' *'
        else:
            labels = ''
            for label in labellist:
                labels += ' ?{}'.format(label)
        return labels

    def _format_body(self, subjectlist = {}):
        body = ''
        numsubjects = len(subjectlist)
        subjectindex = 0
        for subject in subjectlist:
            subjectindex += 1
            # period marks the end of a single subject match
            body += self._format_subject(subject, subjectlist[subject]) + ' .'
            if subjectindex < numsubjects:
                # set each subject on its own line for readability of query
                body += '\n'
        return body

    def _format_subject(self, subject, predlist = {}):
        numpreds = len(predlist['value'])
        predindex = 0
        try:
            if predlist['type'] == 'uri':
                body = '<{}> '.format(subject)
            else:
                body = '?{} '.format(subject)
            for predicate in predlist['value']:
                predindex += 1
                body += self._format_predicate(predicate, predlist['value'][predicate])
                if predindex < numpreds:
                    # semicolon between objects and predicates, none at end
                    body += ' ; '
        except KeyError:
            raise QueryBadFormed(uiLabel.errorSpqrqlQuerySubject)
        return body

    def _format_predicate(self, predicate, objectlist = {}):
        try:
            if objectlist['type'] == 'uri':
                body = '<{}> '.format(predicate)
            else:
                body = '?{} '.format(predicate)
            rdfobjects = objectlist['value']
            numobjects = len(rdfobjects)
            objectindex = 0
            for rdfobject in rdfobjects:
                objectindex += 1
                body += self._format_object(rdfobject)
                if objectindex < numobjects:
                    # comma between consecutive objects, none at end
                    body += ' , '
        except KeyError:
            raise QueryBadFormed(uiLabel.errorSparqlQueryPred)
        return body

    def _format_object(self, rdfobject = {}):
        try:
            if rdfobject['type'] == 'uri':
                body = '<{}>'.format(rdfobject['value'])
            elif rdfobject['type'] == 'label':
                body = '?{}'.format(rdfobject['value'])
            else:
                body = '"{}"'.format(rdfobject['value'])
                if 'xml:lang' in rdfobject:
                    body += '@{}'.format(rdfobject['xml:lang'].lower())
        except KeyError:
            raise QueryBadFormed(uiLabel.errorSparqlQueryObject)
        return body

    def query_general(self, graphlist = [], labellist = [], subjectlist = {}):
        """Return the results of an arbitrarily complex query."""
        prefix = app.config['PREFIXES']
        graphs = self._set_graphs(graphlist)
        labels = self._set_labels(labellist)
        body = self._format_body(subjectlist)
        queryString = """
        {prefix}
        SELECT DISTINCT{labels}
        {graphs}
        WHERE {{
          {body}
        }}
        """.format(prefix=prefix, labels=labels, graphs=graphs, body=body)
        self.setQuery(queryString)
        print(queryString)
        try:
            return self.queryAndConvert()
        except EndPointNotFound:
            raise
        except QueryBadFormed:
            raise
        except EndPointInternalError:
            raise

    def query_user(self, id):
        """Returns the values of a User in the SPARQL endpoint."""
        queryString = """
        {prefix}
        SELECT DISTINCT ?hashpass ?active ?name 
          WHERE {{
            GRAPH <http://localhost/skmf/users> {{
              skmf:{subject} a             skmf:User ;
                             skmf:hashpass ?hashpass ; 
                             skmf:active   ?active ;
                             foaf:name     ?name .
            }}
          }}
        """.format(prefix=app.config['PREFIXES'], subject=id)
        self.setQuery(queryString)
        try:
            return self.queryAndConvert()
        except EndPointNotFound:
            raise
        except QueryBadFormed:
            raise
        except EndPointInternalError:
            raise

    def query_subject(self, id, type = 'uri', graphlist = []):
        """Return all predicates and objects of the subject having id."""
        rdfobject = {'type': 'label', 'value': 'o'}
        predicate = {'p': {'type': 'label', 'value': [rdfobject]}}
        subject = {id: {'type': type, 'value': predicate}}
        labels = ['p', 'o']
        return self.query_general(graphlist, labels, subject)

    def insert(self, graphlist = [], subjectlist = {}):
        prefix = app.config['PREFIXES']
        graphs = graphlist
        if '' not in graphs:
            graphs.append('')
        body = self._format_body(subjectlist)
        for graph in graphs:
            if graph == '':
                graph = app.config['NAMESPACE']
            else:
                graph = app.config['NAMESPACE'] + '/' + graph
            queryString = """
            {prefix}
            INSERT DATA {{
              GRAPH <{graph}> {{
                {body}
              }}
            }}
            """.format(prefix=prefix, graph=graph, body=body)
            print(queryString)
            self.setQuery(queryString)
            self.setMethod(POST)
            try:
                self.query()
            except EndPointNotFound:
                raise
            except QueryBadFormed:
                raise
            except EndPointInternalError:
                raise

    def sparql_insert(self, label, desc):
        """STUB: Insert new data into a SPARQL endpoint."""
        subject = ''.join(c for c in label if c.isalnum()).rstrip()
        queryString = """
        {prefix}
        INSERT DATA {{
          skmf:{subject} rdfs:label "{label}"@en-us ;
                         rdfs:comment "{desc}"@en-us .
        }}
        """.format(prefix=app.config['PREFIXES'],
                   subject=subject, label=label, desc=desc)
        self.setQuery(queryString)
        try:
            self.query()
        except EndPointNotFound:
            raise
        except QueryBadFormed:
            raise
        except EndPointInternalError:
            raise

    def delete(self, graphlist = [], subjectlist = {}):
        prefix = app.config['PREFIXES']
        graphs = graphlist
        if '' not in graphs:
            graphs.append('')
        body = self._format_body(subjectlist)
        for graph in graphs:
            if graph == '':
                graph = app.config['NAMESPACE']
            else:
                graph = app.config['NAMESPACE'] + '/' + graph
            queryString = """
            {prefix}
            DELETE DATA {{
              GRAPH <{graph}> {{
                {body}
              }}
            }}
            """.format(prefix=prefix, graph=graph, body=body)
            print(queryString)
            self.setQuery(queryString)
            self.setMethod(POST)
            try:
                self.query()
            except EndPointNotFound:
                raise
            except QueryBadFormed:
                raise
            except EndPointInternalError:
                raise

    def sparql_delete(endpoint, label):
        """STUB: Delete the specified data from a SPARQL endpoint."""
        queryString = """
        {prefix}
        DELETE {{
          ?s ?plabel ?label ;
             ?pcomment ?comment .
        }}
        WHERE {{
          ?s rdfs:label "{label}" ;
             rdfs:comment ?comment .
        }}
        """.format(prefix=app.config['PREFIXES'], label=label)
        endpoint.setQuery(queryString)
        try:
            endpoint.query()
        except EndPointNotFound:
            raise
        except QueryBadFormed:
            raise
        except EndPointInternalError:
            raise
