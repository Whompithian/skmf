"""skmf.test.test_flask by Brendan Sweeney, CSS 593, 2015.

Provide a set of test cases to verify the correct behavior of the user-facing
portions of the program that are handled by Flask. These views make extensive
use of the SPARQL endpoint connection and, by extension, test much of the
functionality of the SPARQL interface.

Classes:
    BaseTestCase -- Setup class for other TestCase classes.
    FlaskTestCase -- Unit tests to verify correct behavior of Flask views.
"""

import unittest

from flask import Flask, url_for
from flask.ext.bcrypt import Bcrypt
from flask.ext.login import current_user
from flask.ext.testing import TestCase

from skmf import connect_sparql, g
from skmf.resource import Subject
import skmf.i18n.en_US as uiLabel


class BaseTestCase(TestCase):
    """A base test case for common setup tasks.
    
    An extension of the Flask-Testing TestCase that adds methods to be used by
    other tesk cases in this module. No tests are defined. This class is meant
    to be subclassed in order to define actual tests. Any methods defined in
    this class may be safely overridden, so long as create_app properly sets up
    the Flask app.
    
    Methods:
        create_app -- Setup the Flask app and set commonly needed parameters
        login -- Obtain a user session through the login view.
        logout -- Clear a user session through the logout view.
    """

    def create_app(self):
        app = Flask(__name__)
        app.config.from_envvar('FLASK_SETTINGS', silent=False)
        self.bcrypt = Bcrypt(app)
        return app

    def setUp(self):
        g.sparql = connect_sparql()

    def login(self, username, password, follow_redirects = False):
        return self.client.post(url_for('login'), data=dict(
            username=username,
            password=password
        ), follow_redirects=follow_redirects)

    def logout(self):
        return self.client.get(url_for('logout'), follow_redirects=True)


class FlaskTestCase(BaseTestCase):
    """Unit tests to verify the correct behavior of Flask views and databases.
    
    Validate the behavior of template rendering, redirects, session management,
    form handling, error handling, and SPARQL endpoint operations.

    Methods:
        test_login_invalid -- 
        test_login_logout -- 
        test_views_get_responses -- 
        test_view_restricted -- 
    """

    def test_sparql_query_subject(self):
        """Verify that subject query results are correct and complete."""
        id = 'http://localhost/skmf#admin'
        subject = 'http://localhost/skmf#User'
        result = g.sparql.query_subject(id)
        self.assertEqual(len(result['results']['bindings']), 0)
        result = g.sparql.query_subject(subject)
        self.assertNotEqual(len(result['results']['bindings']), 0)
        graphs = ['users']
        result = g.sparql.query_subject(id, *graphs)
        self.assertNotEqual(len(result['results']['bindings']), 0)
        result = g.sparql.query_subject(subject, *graphs)
        self.assertNotEqual(len(result['results']['bindings']), 0)
        result = g.sparql.query_subject('bob', *graphs)
        self.assertEqual(len(result['results']['bindings']), 0)
        graphs.append('bob')
        result = g.sparql.query_subject(id, *graphs)
        self.assertNotEqual(len(result['results']['bindings']), 0)
        graphs.remove('users')
        result = g.sparql.query_subject(id, *graphs)
        self.assertEqual(len(result['results']['bindings']), 0)

    def test_resource_subject(self):
        """Verify that RDF subjects are properly defined and behaved."""
        id = 'http://localhost/skmf#User'
        labelkey = 'http://www.w3.org/2000/01/rdf-schema#label'
        missing = 'http://localhost/skmf#undefined'
        rdfobject = {'value': 'Gone', 'type': 'literal', 'xml:lang': 'en-us'}
        subject = Subject(id)
        self.assertEqual(subject.id, id)
        self.assertIn(labelkey, subject.data)
        clone = Subject(subject.id, **{'type': 'uri', 'value': subject.data})
        self.assertEqual(subject.id, clone.id)
        for predicate in subject.data:
            self.assertEqual(subject.data[predicate], clone.data[predicate])
        subject = Subject(missing)
        self.assertEqual(subject.id, missing)
        self.assertEqual(len(subject.data), 0)
        self.assertNotIn('miss', subject.graphs)
        subject.add_graph('miss')
        self.assertIn('miss', subject.graphs)
        subject.remove_graph('miss')
        self.assertNotIn('miss', subject.graphs)
        subject.add_data(**{labelkey: [rdfobject]})
        self.assertIn(labelkey, subject.data)
        self.assertIn(rdfobject, subject.data[labelkey]['value'])
        clone = Subject(subject.id)
        self.assertIn(labelkey, clone.data)
        self.assertIn(rdfobject, clone.data[labelkey]['value'])
        subject.remove_data(**{labelkey: [rdfobject]})
        self.assertNotIn(labelkey, subject.data)
        clone = Subject(subject.id)
        self.assertNotIn(labelkey, clone.data)

    def test_resource_user(self):
        """Verify that Users are properly defined and behaved."""

    @unittest.skip('Only running backend tests')
    def test_views_get_responses(self):
        self.assert200(self.client.get(url_for('show_tags')))
        self.assertTemplateUsed('show_tags.html')
        self.assertContext('title', uiLabel.viewTagTitle)
        self.assert200(self.client.get(url_for('login')))
        self.assertTemplateUsed('login.html')
        self.assertContext('title', uiLabel.viewLoginTitle)
        self.assert405(self.client.get(url_for('add_tag')))
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

    @unittest.skip('Bypass slow BCrypt functions to speed other tests')
    def test_view_restricted(self):
        """Verify view behavior when user is not logged in."""
        with self.client:
            response = self.client.post(url_for('add_tag'), data=dict(
                label='Label',
                description='A short description.'))
            self.assertRedirects(response, url_for('login') + '?next=%2Fadd')
        with self.client:
            response = self.client.post(url_for('show_users'), data=dict(
                username='bob',
                password='password',
                confirm='password'))
            self.assertRedirects(response, url_for('login') + '?next=%2Fusers')
            self.login('bob', 'default', True)
            self.assertTrue(current_user.is_anonymous)
            self.login('admin', 'default', True)
            self.assert200(self.client.get(url_for('show_users')))
            self.assertTemplateUsed('show_users.html')
            self.assertContext('title', uiLabel.viewUserTitle)

    def test_view_add_tag(self):
        """Verify that tags may be added when user is logged in"""
        pass

    def test_view_create_user(self):
        """Verify that users may be created when admin is logged in"""
        pass

    #with skmf.app.test_request_context('/?name=Peter'):
    #    self.assertEqual(flask.request.path, '/')
    #    self.assertEqual(flask.request.args['name'], 'Peter')

if __name__ == '__main__':
    unittest.main()
