"""skmf.sparqler by Brendan Sweeney, CSS 593, 2015.

Perform operations on a SPARQL endpoint, such as inserts, queries, and updates.
A connection to the endpoint must be passed to each function.
"""

from SPARQLWrapper import JSON, SPARQLExceptions, SPARQLWrapper

from skmf import app
from skmf.i18n.en_US import ISOCode

class SPARQLER(SPARQLWrapper):
    
    def get(endpoint, updateEndpoint):
        sparql = SPARQLER(endpoint=endpoint,
                          updateEndpoint=updateEndpoint,
                          returnFormat=JSON)
        return sparql
    
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

    def sparql_query(self):
        """STUB: Returns the results of a query to a SPARQL endpoint."""
        queryString = """
        {prefix}
        SELECT DISTINCT ?label ?description
        WHERE {{
          ?s rdfs:label ?label ;
             rdfs:comment ?description .
        }}
        """.format(prefix=app.config['PREFIXES'])
        self.setQuery(queryString)
        try:
            return self.queryAndConvert()
        except SPARQLExceptions.EndPointNotFound as d:
            return d.msg
        except SPARQLExceptions.QueryBadFormed as e:
            return e.msg
        except SPARQLExceptions.EndPointInternalError as f:
            return f.msg


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
