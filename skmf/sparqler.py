"""skmf.sparqler by Brendan Sweeney, CSS 593, 2015.

Perform operations on a SPARQL endpoint, such as inserts, queries, and updates.
A connection to the endpoint must have already been established in the global
context, g, with the name, sparql.
"""

from SPARQLWrapper import SPARQLExceptions

from skmf import app, g


def sparql_query():
    """STUB: Returns the results of a query to a SPARQL endpoint."""
    queryString = """
    {prefix}
    SELECT DISTINCT ?label ?description
    WHERE {{
      ?s rdfs:label ?label ;
         rdfs:comment ?description .
    }}
    """.format(prefix=app.config['PREFIXES'])
    g.sparql.setQuery(queryString)
    try:
        return g.sparql.queryAndConvert()
    except SPARQLExceptions.EndPointNotFound as d:
        return d.msg
    except SPARQLExceptions.QueryBadFormed as e:
        return e.msg
    except SPARQLExceptions.EndPointInternalError as f:
        return f.msg


def sparql_insert(label, desc):
    """STUB: Insert new data into a SPARQL endpoint."""
    subject = ''.join(c for c in label if c.isalnum()).rstrip()
    queryString = """
    {prefix}
    INSERT DATA {{
      skmf:{subject} rdfs:label "{label}"@en-US ;
                     rdfs:comment "{desc}"@en-US .
    }}
    """.format(prefix=app.config['PREFIXES'], subject=subject,
               label=label, desc=desc)
    g.update.setQuery(queryString)
    try:
        g.update.query()
    except SPARQLExceptions.EndPointNotFound as d:
        return d.msg
    except SPARQLExceptions.QueryBadFormed as e:
        return e.msg
    except SPARQLExceptions.EndPointInternalError as f:
        return f.msg


def sparql_delete(label):
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
    g.update.setQuery(queryString)
    try:
        g.update.query()
    except SPARQLExceptions.EndPointNotFound as d:
        return d.msg
    except SPARQLExceptions.QueryBadFormed as e:
        return e.msg
    except SPARQLExceptions.EndPointInternalError as f:
        return f.msg
