# unittest in Python 3.4.3 - as of 2015-10-29, no used methods are deprecated
import unittest
from skmf import views

class SemanticKmfTest(unittest.TestCase):

    def test_view_landing_page(self):
        result = views.index()
        self.assertEqual(result, 'Index Page')


if __name__ == '__main__':
    unittest.main()
