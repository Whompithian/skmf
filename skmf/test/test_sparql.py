"""skmf.test_sparql by Brendan Sweeney, CSS 593, 2015.

Provide a set of test cases to verify the correct behavior of the SPARQL end-
point of the program, handled by SPARQLWrapper.

Classes:
SPARQLTestCase -- Unit tests to verify correct behavior of Flask views.
"""

import unittest

from SPARQLWrapper import SPARQLExceptions

from skmf import connect_sparql
#from skmf.sparqler import sparql_query, sparql_insert, sparql_delete


class SPARQLTestCase(unittest.TestCase):
    """Unit tests to verify the correct behavior of the SPARQL endpoint.

    Methods:
    setUp -- Establish a SPARQL endpoint connection.
    test_sparql_connect -- Identify if SPARQL connection fails.
    test_sparql_query_bad -- Identify if truly bad queries are accepted.
    """

    def setUp(self):
        """Establish a SPARQL endpoint connection and default queries."""
        #: Connection to a SPARQL endpoint
        self.sparql = connect_sparql()
        #: Query string that should be rejected by any SPARQL endpoint
        self.query_bad = 'SELECT pie .'
        #: Query string that should be accepted by any SPARQL endpoint
        self.query_good = 'SELECT * WHERE { ?s ?p ?o . } LIMIT 1'

    def test_sparql_query_bad(self):
        """Identify if truly bad queries are accepted by the endpoint."""
        self.sparql.setQuery(self.query_bad)
        with self.assertRaises(SPARQLExceptions.QueryBadFormed):
            self.sparql.query()

    def test_sparql_query_good(self):
        """Identify if good queries are rejected by the endpoint."""
        self.sparql.setQuery(self.query_good)
        results = self.sparql.queryAndConvert()
        self.assertIn('head', results)

    # Currently ouf of context
#    def test_sparql_query_sparqler(self):
#        """."""
#        results = sparql_query()
#        self.assertIn('results', results)

#    def test_sparql_insert_sparqler(self):
#        """."""
#        results = sparql_query()
#        self.assertIn('results', results)
#
#    def test_sparql_delete(self):
#        """."""
#        results = sparql_query()
#        self.assertIn('results', results)


if __name__ == '__main__':
    unittest.main()
