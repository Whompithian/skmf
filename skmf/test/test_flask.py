"""skmf.test_flask by Armin Ronacher
(Modified by Brendan Sweeney, CSS 593, 2015.)

Provide a set of test cases to verify the correct behavior of the user-facing
portions of the program that are handled by Flask. Currently, this is taken
from the Flaskr tutorial and will need to be modified as the frontend of the
system is developed.

Classes:
FlaskTestCase -- Unit tests to verify correct behavior of Flask views.
"""

#import os
import unittest
#import tempfile

from flask import url_for
from flask.ext.bcrypt import Bcrypt
from flask.ext.login import current_user
from flask.ext.testing import TestCase

from skmf import app
import skmf.i18n.en_US as lang


class BaseTestCase(TestCase):
    """A base test case for flask-tracking."""

    def create_app(self):
        app.config.from_envvar('FLASKR_SETTINGS', silent=False)
        self.bcrypt = Bcrypt(app)
        return app

    def login(self, username, password, follow_redirects = False):
        return self.client.post(url_for('login'), data=dict(
            username=username,
            password=password
        ), follow_redirects=follow_redirects)

    def logout(self):
        return self.client.get(url_for('logout'), follow_redirects=True)

#    def setUp(self):
#        self.db_fd, skmf.app.config['DATABASE'] = tempfile.mkstemp()
#        skmf.app.config['TESTING'] = True
#        self.app = skmf.app.test_client()
#        skmf.init_db()
#
#    def tearDown(self):
#        os.close(self.db_fd)
#        os.unlink(skmf.app.config['DATABASE'])


class FlaskTestCase(BaseTestCase):
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

    def test_views_get_responses(self):
        self.assert200(self.client.get(url_for('show_entries')))
        self.assertTemplateUsed('show_entries.html')
        self.assertContext('title', 'Flaskr')
        self.assert200(self.client.get(url_for('show_tags')))
        self.assertTemplateUsed('show_tags.html')
        self.assertContext('title', lang.viewTagTitle)
        self.assert200(self.client.get(url_for('login')))
        self.assertTemplateUsed('login.html')
        self.assertContext('title', lang.viewLoginTitle)
        response = self.client.get(url_for('show_users'))
        self.assertRedirects(response, url_for('login') + '?next=%2Fusers')

    @unittest.skip('Bypass slow BCrypt functions to speed other tests')
    def test_login_logout(self):
        with self.client:
            self.assertTrue(current_user.is_anonymous)
            self.login('admin', 'default')
            self.assertEqual(current_user.get_id(), 'admin')
            self.assertTrue(self.bcrypt.check_password_hash(
                                    current_user.hashpass, 'default'))
            self.assertEqual(current_user.get_name(), 'Administrator')
            self.assertTrue(current_user.is_authenticated())
            self.assertTrue(current_user.is_active())
            self.assertFalse(current_user.is_anonymous())
            response = self.logout()
            self.assertTrue(current_user.is_anonymous)
            self.assertIn('You were logged out', response.data.decode('utf-8'))

    @unittest.skip('Bypass slow BCrypt functions to speed other tests')
    def test_login_invalid(self):
        with self.client:
            response = self.login('Admin', 'default', True)
            self.assertTrue(current_user.is_anonymous)
            self.assertIn('Invalid username or password',
                          response.data.decode('utf-8'))
        with self.client:
            response = self.login('admin', 'dEfAuLt', True)
            self.assertTrue(current_user.is_anonymous)
            self.assertIn('Invalid username or password',
                          response.data.decode('utf-8'))

    def test_view_while_logged_in(self):
        """Verify view behavior when user is logged in"""
        with self.client:
            response = self.client.post(url_for('show_users'), data=dict(
                username='bob',
                password='password',
                confirm='password'
            ), follow_redirects=True)
            self.assert200(response)
            self.assertTemplateUsed('login.html')
            self.assertContext('title', lang.viewLoginTitle)
            self.login('bob', 'default', True)
            self.assertTrue(current_user.is_anonymous)
            self.login('admin', 'default', True)
            self.assert200(self.client.get(url_for('show_users')))
            self.assertTemplateUsed('show_users.html')
            self.assertContext('title', lang.viewUserTitle)
#            self.assert200(response)
#            self.login('admin', 'default', True)
#            response = self.client.get('/tags')
#            self.assertIn('Manage Tags', response.data.decode('utf-8'))

#    def test_messages(self):
#        self.login('admin', 'default')
#        rv = self.client.post('/add', data=dict(
#            title='<Hello>',
#            text='<strong>HTML</strong> allowed here'
#        ), follow_redirects=True)
#        self.assertNotIn('No entries here so far', rv.data.decode('utf-8'))
#        self.assertIn('&lt;Hello&gt;', rv.data.decode('utf-8'))
#        self.assertIn('<strong>HTML</strong> allowed here',
#                      rv.data.decode('utf-8'))

    #with skmf.app.test_request_context('/?name=Peter'):
    #    self.assertEqual(flask.request.path, '/')
    #    self.assertEqual(flask.request.args['name'], 'Peter')

if __name__ == '__main__':
    unittest.main()
