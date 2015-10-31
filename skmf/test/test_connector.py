import unittest
from skmf import views

class SemanticKmfTest(unittest.TestCase):

    def test_view_landing_page(self):
        result = views.index()
        self.assertEqual(result, 'Hello, World!')


if __name__ == '__main__':
    unittest.main()
