"""skmf.test.test_flask by Brendan Sweeney, CSS 593, 2015.

Provide a set of test cases to verify the correct behavior of the user-facing
portions of the program that are handled by Flask. These views make extensive
use of the SPARQL endpoint connection and, by extension, test much of the
functionality of the SPARQL interface.

Classes:
    BaseTestCase: Setup class for other TestCase classes.
    FlaskTestCase: Unit tests to verify correct behavior of Flask views.
    SPARQLERTestCase: 
    ResourceQueryTestCase: 
    ResourceSubjectTestCase:
    ResourceUserTestCase: 
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


class SPARQLERTestCase(BaseTestCase):
    """Unit tests to verify the correct behavior of Flask views and databases.
    
    Validate the behavior of template rendering, redirects, session management,
    form handling, error handling, and SPARQL endpoint operations.
    """

    def test_sparql_query_subject(self):
        """Verify that subject query results are correct and complete."""
        id = 'http://localhost/skmf#admin'
        subject = 'http://localhost/skmf#User'
        result = g.sparql.query_subject(id)
        # admin user not defined in the default graph
        self.assertFalse(result['results']['bindings'])
        result = g.sparql.query_subject(subject)
        # skmf:User is defined in the default graph
        self.assertTrue(result['results']['bindings'])
        graphs = {'users'}
        result = g.sparql.query_subject(id, 'uri', graphs)
        # admin user is defined in the users graph
        self.assertTrue(result['results']['bindings'])
        result = g.sparql.query_subject(subject, 'uri', graphs)
        # skmf:User not defined in the users graph
        self.assertFalse(result['results']['bindings'])
        graphs.add('')
        result = g.sparql.query_subject(subject, 'uri', graphs)
        # skmf:User is defined in a provided graph
        self.assertTrue(result['results']['bindings'])
        result = g.sparql.query_subject('bob', 'uri', graphs)
        # 'bob' not defined in any graphs
        self.assertFalse(result['results']['bindings'])
        graphs.add('bob')
        result = g.sparql.query_subject(id, 'uri', graphs)
        # addition of 'bob' graph does not hide admin user
        self.assertTrue(result['results']['bindings'])
        graphs.discard('users')
        result = g.sparql.query_subject(id, 'uri', graphs)
        # removal of 'users' graph does hide admin user
        self.assertFalse(result['results']['bindings'])


class ResourceQueryTestCase(BaseTestCase):
    """Unit tests to verify the correct behavior of Flask views and databases.
    
    Validate the behavior of template rendering, redirects, session management,
    form handling, error handling, and SPARQL endpoint operations.
    """


class ResourceSubjectTestCase(BaseTestCase):
    """Unit tests to verify the correct behavior of Flask views and databases.
    
    Validate the behavior of template rendering, redirects, session management,
    form handling, error handling, and SPARQL endpoint operations.
    """

    def test_resource_subject(self):
        """Verify that RDF subjects are properly defined and behaved."""
        id = 'http://localhost/skmf#User'
        labelkey = 'http://www.w3.org/2000/01/rdf-schema#label'
        missing = 'http://localhost/skmf#undefined'
        rdfobject = {'value': 'Gone', 'type': 'literal', 'xml:lang': 'en-us'}
        predlist = {labelkey: {'type': 'uri', 'value': [rdfobject]}}
        subject = Subject(id)
        # skmf:User should be read from triplestore with expected values
        self.assertEqual(subject.id, id)
        self.assertIn(labelkey, subject.preds)
        clone = Subject(subject.id, predlist=subject.preds)
        # All values of 'clone' should match those of the copied 'subject'
        self.assertEqual(subject.id, clone.id)
        for predicate in subject.preds:
            self.assertEqual(subject.preds[predicate], clone.preds[predicate])
        miss = Subject(missing)
        # skmf:undefined should not be found in the triplestore, empty subject
        self.assertEqual(miss.id, missing)
        self.assertFalse(miss.preds)
        self.assertNotIn('miss', miss.graphs)
        miss.add_graphs({'miss'})
        # graph 'miss' should be in 'graphs' list
        self.assertIn('miss', miss.graphs)
        miss.remove_graphs({'miss'})
        # graph 'miss' should no longer be in 'graphs' list
        self.assertNotIn('miss', miss.graphs)
        miss.add_data(graphlist={''}, predlist=predlist)
        # data should appear in object
        self.assertIn(labelkey, miss.preds)
        self.assertIn(rdfobject, miss.preds[labelkey]['value'])
        clone = Subject(miss.id)
        # 'clone' should have pulled added data from triplestore
        self.assertIn(labelkey, clone.preds)
        self.assertIn(rdfobject, clone.preds[labelkey]['value'])
        miss.remove_data(graphlist={''}, predlist=predlist)
        # data should no longer appear in object
        self.assertNotIn(labelkey, miss.preds)
        clone = Subject(miss.id)
        # 'clone' should no longer pull removed data from triplestore
        self.assertNotIn(labelkey, clone.preds)


class ResourceUserTestCase(BaseTestCase):
    """Unit tests to verify the correct behavior of Flask views and databases.
    
    Validate the behavior of template rendering, redirects, session management,
    form handling, error handling, and SPARQL endpoint operations.
    """

    def test_resource_user(self):
        """Verify that Users are properly defined and behaved."""


class FlaskTestCase(BaseTestCase):
    """Unit tests to verify the correct behavior of Flask views and databases.
    
    Validate the behavior of template rendering, redirects, session management,
    form handling, error handling, and SPARQL endpoint operations.
    """

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
