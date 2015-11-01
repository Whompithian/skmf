# unittest in Python 3.4.3 - as of 2015-10-29, no used methods are deprecated
import unittest
from SPARQLWrapper import SPARQLExceptions

from skmf import connect_sparql #, views


class SemanticKMFTest(unittest.TestCase):
    
    def setUp(self):
        self.sparql = connect_sparql()
        self.query_bad = 'SELECT pie.'
        self.query_good = 'SELECT * WHERE { ?s ?p ?o. } LIMIT 1'

#    def test_html_header(self):
#        header = '<!doctype html>'
#        result = views.show_entries()
#        self.assertIn(header, result)

#    def test_view_landing_page(self):
#        result = views.index()
#        self.assertEqual(result, 'Index Page')

    def test_sparql_connect(self):
        self.assertIsNotNone(self.sparql)

    def test_sparql_query_bad(self):
        self.sparql.setQuery(self.query_bad)
        with self.assertRaises(SPARQLExceptions.QueryBadFormed):
            self.sparql.query()


if __name__ == '__main__':
    unittest.main()
