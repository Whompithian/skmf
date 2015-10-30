import unittest
from skmf.views import View

class SemanticKmfTest(unittest.TestCase):

    def test_view_landing_page(self):
        view = View()
        result = view.index()
        self.assertEqual(result, 'Hello, World!')


if __name__ == '__main__':
    unittest.main()
