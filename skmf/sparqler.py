from skmf import app, g

def sparql_query():
    queryString = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skmf: NAMESPACE
    SELECT DISTINCT ?label ?description
    WHERE {
      ?s rdfs:label ?label ;
         rdfs:comment ?description .
    }
    """
    queryString = queryString.replace('NAMESPACE', app.config['NAMESPACE'])
    g.sparql.setQuery(queryString)
    try:
        return g.sparql.query().convert()
    except Exception as e:
        return str(e)


def sparql_update(label, desc):
    subject = ''.join(c for c in label if c.isalnum()).rstrip()
    queryString = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skmf: NAMESPACE
    INSERT DATA {
      skmf:SUBJECT rdfs:label "LABEL"@en-US ;
                   rdfs:comment "DESC"@en-US .
    }
    """
    queryString = queryString.replace('NAMESPACE', app.config['NAMESPACE'])
    queryString = queryString.replace('SUBJECT', subject)
    queryString = queryString.replace('LABEL', label)
    queryString = queryString.replace('DESC', desc)
    g.update.setQuery(queryString)
    try:
        g.update.query()
    except Exception as e:
        return(str(e))
