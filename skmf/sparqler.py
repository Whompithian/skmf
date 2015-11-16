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

from SPARQLWrapper import JSON, POST, SPARQLExceptions, SPARQLWrapper

from skmf import app
from skmf.i18n.en_US import ISOCode

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

    def _set_graphs(self, *args):
        graphs = 'FROM <{namespace}>'.format(namespace=app.config['NAMESPACE'])
        for graph in args:
            graph = app.config['NAMESPACE'] + '/' + graph
            graphs += '\nFROM <{graph}>'.format(graph=graph)
        return graphs

    def _format_body(self, **kwargs):
        body = ''
        numsubjects = len(kwargs)
        subjectindex = 0
        for subject in kwargs:
            subjectindex += 1
            try:
                # period marks the end of a single subject match
                body += self._format_subject(subject, **kwargs[subject]) + ' .'
                if subjectindex < numsubjects:
                    # set each subject on its own line for readability of query
                    body += '\n'
            except KeyError:
                raise SPARQLExceptions.QueryBadFormed('subject must have value')
        return body

    def _format_subject(self, subject, **kwargs):
        numpreds = len(kwargs['value'])
        predindex = 0
        try:
            if kwargs['type'] == 'uri':
                body = '<{}> '.format(subject)
            else:
                body = '?{} '.format(subject)
            for predicate in kwargs['value']:
                predindex += 1
                body += self._format_predicate(predicate, **kwargs['value'][predicate])
                if predindex < numpreds:
                    # semicolon between objects and predicates, none at end
                    body += ' ; '
        except KeyError:
            raise SPARQLExceptions.QueryBadFormed('bad subject definition')
        return body

    def _format_predicate(self, predicate, **kwargs):
        try:
            if kwargs['type'] == 'uri':
                body = '<{}> '.format(predicate)
            else:
                body = '?{} '.format(predicate)
            rdfobjects = kwargs['value']
            numobjects = len(rdfobjects)
            objectindex = 0
            for rdfobject in rdfobjects:
                objectindex += 1
                body += self._format_object(**rdfobject)
                if objectindex < numobjects:
                    # comma between consecutive objects, none at end
                    body += ' , '
        except KeyError:
            raise SPARQLExceptions.QueryBadFormed('bad predicate definition')
        return body

    def _format_object(self, **kwargs):
        try:
            if kwargs['type'] == 'uri':
                body = '<{}>'.format(kwargs['value'])
            elif kwargs['type'] == 'label':
                body = '?{}'.format(kwargs['value'])
            else:
                body = '"{}"'.format(kwargs['value'])
                if 'xml:lang' in kwargs:
                    body += '@{}'.format(kwargs['xml:lang'].lower())
        except KeyError:
            # query bad formed, not recoverable
            raise SPARQLExceptions.QueryBadFormed('bad object definition')
        return body

    def query_general(self, *args, **kwargs):
        """Return the results of an arbitrarily complex query."""
        graphs = self._set_graphs(*args)
        labels = ''
        if 'labels' not in kwargs:
            raise SPARQLExceptions.QueryBadFormed('select requires labels')
        for label in kwargs['labels']:
            labels += ' ?' + label
        if 'terms' not in kwargs:
            raise SPARQLExceptions.QueryBadFormed('select requires labels')
        body = self._format_body(**kwargs['terms'])
        queryString = """
        {prefix}
        SELECT DISTINCT{labels}
        {graphs}
        WHERE {{
          {body}
        }}
        """.format(prefix=app.config['PREFIXES'], labels=labels, graphs=graphs, body=body)
        self.setQuery(queryString)
        print(queryString)
        try:
            return self.queryAndConvert()
        except SPARQLExceptions.EndPointNotFound as d:
            return d.msg
        except SPARQLExceptions.QueryBadFormed as e:
            return e.msg
        except SPARQLExceptions.EndPointInternalError as f:
            return f.msg

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
        except SPARQLExceptions.EndPointNotFound as d:
            return d.msg
        except SPARQLExceptions.QueryBadFormed as e:
            return e.msg
        except SPARQLExceptions.EndPointInternalError as f:
            return f.msg

    def query_subject(self, id, *args):
        """Return all predicates and objects of the subject having id."""
        rdfobject = {'value': 'o', 'type': 'label'}
        predicate = {'p': {'type': 'label', 'value': [rdfobject]}}
        subject = {id: {'type': 'uri', 'value': predicate}}
        query = {'labels': ['p', 'o'], 'terms': subject}
        return self.query_general(*args, **query)

    def insert(self, *args, **kwargs):
        graphs = []
        if args:
            graphs = args
        if '' not in graphs:
            graphs.append('')
        body = self._format_body(**kwargs)
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
            """.format(prefix=app.config['PREFIXES'], graph=graph, body=body)
            print(queryString)
            self.setQuery(queryString)
            self.setMethod(POST)
            try:
                self.query()
            except SPARQLExceptions.EndPointNotFound as d:
                print(d.msg)
            except SPARQLExceptions.QueryBadFormed as e:
                print(e.msg)
            except SPARQLExceptions.EndPointInternalError as f:
                print(f.msg)

    def sparql_insert(self, label, desc):
        """STUB: Insert new data into a SPARQL endpoint."""
        subject = ''.join(c for c in label if c.isalnum()).rstrip()
        queryString = """
        {prefix}
        INSERT DATA {{
          skmf:{subject} rdfs:label "{label}"@{iso} ;
                         rdfs:comment "{desc}"@{iso} .
        }}
        """.format(prefix=app.config['PREFIXES'],
                   subject=subject, label=label, desc=desc, iso=ISOCode)
        self.setQuery(queryString)
        try:
            self.query()
        except SPARQLExceptions.EndPointNotFound as d:
            return d.msg
        except SPARQLExceptions.QueryBadFormed as e:
            return e.msg
        except SPARQLExceptions.EndPointInternalError as f:
            return f.msg

    def delete(self, *args, **kwargs):
        graphs = []
        if args:
            graphs = args
        if '' not in graphs:
            graphs.append('')
        body = self._format_body(**kwargs)
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
            """.format(prefix=app.config['PREFIXES'], graph=graph, body=body)
            print(queryString)
            self.setQuery(queryString)
            self.setMethod(POST)
            try:
                self.query()
            except SPARQLExceptions.EndPointNotFound as d:
                print(d.msg)
            except SPARQLExceptions.QueryBadFormed as e:
                print(e.msg)
            except SPARQLExceptions.EndPointInternalError as f:
                print(f.msg)

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
        except SPARQLExceptions.EndPointNotFound as d:
            return d.msg
        except SPARQLExceptions.QueryBadFormed as e:
            return e.msg
        except SPARQLExceptions.EndPointInternalError as f:
            return f.msg
