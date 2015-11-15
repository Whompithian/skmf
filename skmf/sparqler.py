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

    def set_graphs(self, *args):
        graphs = 'FROM <{namespace}>'.format(namespace=app.config['NAMESPACE'])
        for graph in args:
            graph = app.config['NAMESPACE'] + '/' + graph
            graphs += '\nFROM <{graph}>'.format(graph=graph)
        return graphs

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
        graphs = self.set_graphs(*args)
        queryString = """
        {prefix}
        SELECT DISTINCT ?p ?o
        {graphs}
        WHERE {{
          <{subject}> ?p ?o .
        }}
        """.format(prefix=app.config['PREFIXES'], graphs=graphs, subject=id)
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

    def format_body(self, **kwargs):
        body = ''
        numsubjects = len(kwargs)
        subjectindex = 0
        for subject in kwargs:
            subjectindex += 1
            body += '<{}> '.format(subject)
            numpreds = len(kwargs[subject])
            predindex = 0
            for predicate in kwargs[subject]:
                predindex += 1
                body += '<{}> '.format(predicate)
                rdfobjects = kwargs[subject][predicate]
                numobjects = len(rdfobjects)
                objectindex = 0
                for rdfobject in rdfobjects:
                    objectindex += 1
                    if rdfobject.type == 'uri':
                        body += '<{}>'.format(rdfobject.value)
                    else:
                        body += '"{}"'.format(rdfobject.value)
                        if rdfobject.xmllang:
                            body += '@{}'.format(rdfobject.xmllang)
                    body += ' '
                    if objectindex < numobjects:
                        body += ', '
                if predindex < numpreds:
                    body += '; '
            body += '.'
            if subjectindex < numsubjects:
                body += '\n'
        return body

    def insert(self, *args, **kwargs):
        graphs = []
        if args:
            graphs = args
        if '' not in graphs:
            graphs.append('')
        body = self.format_body(**kwargs)
        for graph in graphs:
            graph = app.config['NAMESPACE'] + graph
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
        body = self.format_body(**kwargs)
        for graph in graphs:
            graph = app.config['NAMESPACE'] + graph
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
