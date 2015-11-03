"""skmf.test_flask by Armin Ronacher
(Modified by Brendan Sweeney, CSS 593, 2015.)

Provide a set of test cases to verify the correct behavior of the user-facing
portions of the program that are handled by Flask. Currently, this is taken
from the Flaskr tutorial and will need to be modified as the frontend of the
system is developed.

Classes:
FlaskTestCase -- Unit tests to verify correct behavior of Flask views.
"""

import os
import unittest
import tempfile

import skmf


class FlaskTestCase(unittest.TestCase):
    """Unit tests to verify the correct behavior of Flask views and databases.

    Methods:
    login -- Return the login status view after attempting to login a user.
    logout -- Return the logout status view after logging out a user.
    setUp -- Establish a database connection and switch on testing mode.
    tearDown -- Close the database and its associated file.
    test_empty_db -- Identify if the database seems not to be empty.
    test_login_logout -- Identify if login does not work properly.
    test_message -- Identify if messages are not filtered as expected.
    """

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def setUp(self):
        self.db_fd, skmf.app.config['DATABASE'] = tempfile.mkstemp()
        skmf.app.config['TESTING'] = True
        self.app = skmf.app.test_client()
        skmf.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(skmf.app.config['DATABASE'])

    def test_empty_db(self):
        rv = self.app.get('/')
        self.assertIn('No entries here so far', rv.data.decode('utf-8'))

    def test_login_logout(self):
        rv = self.login('admin', 'default')
        self.assertIn('You were logged in', rv.data.decode('utf-8'))
        rv = self.logout()
        self.assertIn('You were logged out', rv.data.decode('utf-8'))
        rv = self.login('adminx', 'default')
        self.assertIn('Invalid username', rv.data.decode('utf-8'))
        rv = self.login('admin', 'defaultx')
        self.assertIn('Invalid password', rv.data.decode('utf-8'))

    def test_messages(self):
        self.login('admin', 'default')
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here'
        ), follow_redirects=True)
        self.assertNotIn('No entries here so far', rv.data.decode('utf-8'))
        self.assertIn('&lt;Hello&gt;', rv.data.decode('utf-8'))
        self.assertIn('<strong>HTML</strong> allowed here',
                      rv.data.decode('utf-8'))

    def test_show_tags_page(self):
        """Identify any issues loading the 'tags' view"""
        self.login('admin', 'default')
        rv = self.app.get('/tags')
        self.assertIn('Manage Tags', rv.data.decode('utf-8'))

    #def test_html_header(self):
    #    header = '<!doctype html>'
    #    result = views.show_entries()
    #    self.assertIn(header, result)

    #with skmf.app.test_request_context('/?name=Peter'):
    #    self.assertEqual(flask.request.path, '/')
    #    self.assertEqual(flask.request.args['name'], 'Peter')

if __name__ == '__main__':
    unittest.main()
