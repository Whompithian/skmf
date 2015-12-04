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

from flask import url_for
from flask.ext.bcrypt import Bcrypt
from flask.ext.login import current_user
from flask.ext.testing import TestCase

from skmf import app, connect_sparql, g
from skmf.resource import Query, Subject, User
import skmf.i18n.en_US as uiLabel


constraint = {'http://localhost/skmf#id':
               {'type': 'uri',
                'value':
                 {'http://www.w3.org/2000/01/rdf-schema#comment':
                   {'type': 'uri',
                    'value':
                     [{'type': 'literal',
                       'value': 'A unique string to identify a registered user.',
                       'xml:lang': 'EN-US'
                     },
                     {'type': 'literal',
                       'value': 'A unique string to identify a registered user.',
                       'xml:lang': 'EN-US'
                     }, 
                     {'type': 'literal',
                       'value': 'A unique string to identify a registered user.',
                       'xml:lang': 'EN-US'
                     }]
                   },
                  'http://www.w3.org/2000/01/rdf-schema#label':
                   {'type': 'uri',
                    'value': 
                     [{'type': 'literal',
                       'value': 'UserID',
                       'xml:lang': 'EN-US'
                     }]
                   },
                  'http://www.w3.org/1999/02/22-rdf-syntax-ns#type':
                   {'type': 'uri',
                    'value':
                     [{'type': 'uri',
                       'value': 'http://www.w3.org/2000/01/rdf-schema#Class'
                     }]
                   },
                  'http://www.w3.org/2000/01/rdf-schema#isDefinedBy':
                   {'type': 'uri',
                    'value':
                     [{'type': 'uri',
                       'value': 'http://localhost/skmf#'
                     }]
                   }
                 }
               },
              'http://example.com/blah#bleh':
               {'type': 'uri',
                'value':
                 {'http://www.w3.org/2000/01/rdf-schema#comment':
                   {'type': 'uri',
                    'value':
                     [{'type': 'literal',
                       'value': 'A unique string to identify a registered user.',
                       'xml:lang': 'EN-US'
                     }]
                   },
                  'http://www.w3.org/2000/01/rdf-schema#label':
                   {'type': 'uri',
                    'value': 
                     [{'type': 'literal',
                       'value': 'UserID',
                       'xml:lang': 'EN-US'
                     }]
                   },
                  'http://www.w3.org/1999/02/22-rdf-syntax-ns#type':
                   {'type': 'uri',
                    'value':
                     [{'type': 'uri',
                       'value': 'http://www.w3.org/2000/01/rdf-schema#Class'
                     }]
                   },
                  'http://www.w3.org/2000/01/rdf-schema#isDefinedBy':
                   {'type': 'uri',
                    'value':
                     [{'type': 'uri',
                       'value': 'http://localhost/skmf#'
                     }]
                   }
                 }
               },
              'http://localhost/skmf#admin':
               {'type': 'uri',
                'value':
                 {'http://localhost/skmf#id':
                   {'type': 'uri',
                    'value':
                     [{'type': 'literal',
                       'value': 'admin'
                     }]
                   }
                 }
               },
              'http://localhost/skmf#User':
               {'type': 'uri',
                'value':
                 {'http://www.w3.org/2000/01/rdf-schema#member':
                   {'type': 'uri',
                    'value':
                     [{'type': 'uri',
                       'value': 'http://localhost/skmf#id'
                     }]
                   }
                 }
               }
             }


class BaseTestCase(TestCase):
    """A base test case for common setup tasks.
    
    An extension of the Flask-Testing TestCase that adds methods to be used by
    other tesk cases in this module. No tests are defined. This class is meant
    to be subclassed in order to define actual tests. Any methods defined in
    this class may be safely overridden, so long as create_app properly sets up
    the Flask app.
    """

    def create_app(self):
        """Initialize the Flask application with a testing configuration."""
        app.config.from_envvar('FLASK_SETTINGS', silent=False)
        self.bcrypt = Bcrypt(app)
        return app

    def setUp(self):
        """Establish a connection to the SPARQL endpoint."""
        g.sparql = connect_sparql()

    def login(self, username, password, follow_redirects = False):
        """Perform a login operation for the provided user.
        
        This is basically a placeholder for the user login form Web page.
        
        Args:
            follow_redirects (bool): Whether to follow view redirects.
            password (str): Plain text password of the user to login.
            username (str): Unique ID of the user to login.
        
        Returns:
            The view provided by the login submission.
        """
        return self.client.post(url_for('login'), data=dict(
            username=username,
            password=password
        ), follow_redirects=follow_redirects)

    def logout(self):
        """Perform a logout of the current user, if logged in."""
        return self.client.get(url_for('logout'), follow_redirects=True)


class SPARQLERTestCase(BaseTestCase):
    """Unit tests to verify the correct behavior of SPARQLER CRUD events.
    
    Validate the behavior of SPARQL endpoint operations.
    """
    
    id = 'http://localhost/skmf#admin'
    rdfs_class = 'http://www.w3.org/2000/01/rdf-schema#Class'
    subject = 'http://localhost/skmf#User'

    def test_sparql_query_subject(self):
        """Verify that subject query results are correct and complete."""
        g.sparql.query_general({'', 'blah', 'bleh', 'bluh'},
                               {'bob', 'bub', 'bib'}, constraint)
        result = g.sparql.query_subject(self.id)
        # admin user not defined in the default graph
        self.assertFalse(result['results']['bindings'])
        result = g.sparql.query_subject(self.subject)
        # skmf:User is defined in the default graph
        self.assertTrue(result['results']['bindings'])
        graphs = {'users'}
        result = g.sparql.query_subject(self.id, 'uri', graphs)
        # admin user is defined in the users graph
        self.assertTrue(result['results']['bindings'])
        result = g.sparql.query_subject(self.subject, 'uri', graphs)
        # skmf:User not defined in the users graph
        self.assertFalse(result['results']['bindings'])
        graphs.add('')
        result = g.sparql.query_subject(self.subject, 'uri', graphs)
        # skmf:User is defined in a provided graph
        self.assertTrue(result['results']['bindings'])
        result = g.sparql.query_subject('bob', 'uri', graphs)
        # 'bob' not defined in any graphs
        self.assertFalse(result['results']['bindings'])
        graphs.add('bob')
        result = g.sparql.query_subject(self.id, 'uri', graphs)
        # addition of 'bob' graph does not hide admin user
        self.assertTrue(result['results']['bindings'])
        graphs.discard('users')
        result = g.sparql.query_subject(self.id, 'uri', graphs)
        # removal of 'users' graph does hide admin user
        self.assertFalse(result['results']['bindings'])

    def test_sparql_query_general(self):
        """Verify that general query results are correct and complete."""
        labels = {'s', 'p', 'o'}
        subjects = {'s':
                       {'type': 'label',
                        'value':
                            {'p':
                                {'type': 'label',
                                 'value':
                                     [{'type': 'label',
                                     'value': 'o'}]}}}}
        user_subject = {'skmf:User':
                           {'type': 'pfx',
                            'value':
                                {'a':
                                    {'type': 'pfx',
                                     'value':
                                         [{'type': 'label',
                                           'value': 'o'}]}}}}
        opt_pred = {'rdfs:label': 
                       {'type': 'pfx',
                        'value':
                            [{'type': 'label',
                              'value': 'label'}]}}
        opt_subject = {'o':
                        {'type': 'label',
                         'value': opt_pred}}
        result = g.sparql.query_general()
        # empty query is valid
        self.assertFalse(result['results']['bindings'])
        result = g.sparql.query_general(labellist=labels, subjectlist=subjects)
        # labeled items should be in results
        self.assertIn('s', result['head']['vars'])
        self.assertIn('p', result['head']['vars'])
        self.assertIn('o', result['head']['vars'])
        result_no_labels = g.sparql.query_general(subjectlist=subjects)
        # empty label list should return all labels from subject list
        self.assertIn('s', result_no_labels['head']['vars'])
        self.assertIn('p', result_no_labels['head']['vars'])
        self.assertIn('o', result_no_labels['head']['vars'])
        result_user = g.sparql.query_general(subjectlist=user_subject)
        # skmf:User should have a type property of rdfs:Class
        self.assertNotIn('s', result_user['head']['vars'])
        self.assertNotIn('p', result_user['head']['vars'])
        self.assertIn('o', result_user['head']['vars'])
        self.assertIn(self.rdfs_class,
                      result_user['results']['bindings'][0]['o']['value'])
        user_subject['o'] = {'type': 'label', 'value': opt_pred}
        result_mixed = g.sparql.query_general(subjectlist=user_subject)
        # no label for rdfs:Class in skmf, so no results from query
        self.assertFalse(result_mixed['results']['bindings'])
        del user_subject['o']
        result_mixed = g.sparql.query_general(subjectlist=user_subject,
                                              optlist=[opt_subject])
        # making the label portion optional allows results to be returned
        self.assertTrue(result_mixed['results']['bindings'])

    def test_sparql_insert_delete(self):
        """Verify that INSERT and DELETE are correct and complementary."""
        new_subject = {'skmf:blah':
                       {'type': 'pfx',
                        'value': 
                            {'skmf:bleh':
                                {'type': 'pfx',
                                 'value':
                                     [{'type': 'pfx',
                                       'value': 'skmf:bluh'}]}}}}
        test_subject = {'skmf:blah':
                        {'type': 'pfx',
                         'value': 
                             {'p':
                                 {'type': 'label',
                                  'value':
                                      [{'type': 'label',
                                        'value': 'o'}]}}}}
        result_empty = g.sparql.query_general(subjectlist=test_subject)
        # skmf:blah does not yet exist in the triplestore
        self.assertFalse(result_empty['results']['bindings'])
        g.sparql.insert(graphlist={''}, subjectlist=new_subject)
        result = g.sparql.query_general(subjectlist=test_subject)
        # skmf:blah has been added to the triplestore
        self.assertTrue(result['results']['bindings'])
        g.sparql.delete(graphlist={''}, subjectlist=new_subject)
        result_empty_again = g.sparql.query_general(subjectlist=test_subject)
        # skmf:blah does not yet exist in the triplestore
        self.assertFalse(result_empty_again['results']['bindings'])


class ResourceQueryTestCase(BaseTestCase):
    """Unit tests to verify correct behavior of Query instances and methods.
    
    Validate the behavior of middleware for SPARQL endpoint operations.
    """

    def test_resource_query(self):
        """Verify that queries are properly defined and behaved."""
        query = Query()
        self.assertIn('', query.graphs)
        self.assertFalse(query.labels)
        self.assertFalse(query.subjects)
        self.assertNotIn('bob', query.graphs)
        query.add_graphs({'bob'})
        self.assertIn('bob', query.graphs)
        query.remove_graphs({'bob'})
        self.assertNotIn('bob', query.graphs)
        query.add_graphs({'users'})
        local_constraint = {'s':
                               {'type': 'label',
                                'value':
                                    {'p':
                                        {'type': 'label',
                                         'value':
                                             [{'type': 'label',
                                               'value': 'o'}]}}}}
        query.add_constraints(labellist={'s', 'p', 'o'},
                              subjectlist=local_constraint)
        query.remove_constraints(labellist={'s', 'p', 'o'},
                                 subjectlist=local_constraint)
        self.assertFalse(query.labels)
        self.assertFalse(query.subjects)
        query.remove_graphs({'users'})
        query.add_constraints(subjectlist=constraint)
        query.submit_delete()
        query.remove_constraints(subjectlist=constraint)
        query.add_constraints(subjectlist=constraint)
        query.submit_delete()
        query.remove_constraints(subjectlist=constraint)


class ResourceSubjectTestCase(BaseTestCase):
    """Unit tests to verify correct behavior of RDF Subjects and methods.
    
    Validate the behavior of middleware for SPARQL endpoint operations.
    """
    
    id = 'http://localhost/skmf#User'
    labelkey = 'http://www.w3.org/2000/01/rdf-schema#label'
    missing = 'http://localhost/skmf#undefined'
    rdfobject = {'value': 'Gone', 'type': 'literal', 'xml:lang': 'en-us'}
    predlist = {labelkey: {'type': 'uri', 'value': [rdfobject]}}

    def test_resource_subject(self):
        """Verify that RDF subjects are properly defined and behaved."""
        subject = Subject(self.id)
        # skmf:User should be read from triplestore with expected values
        self.assertEqual(subject.id, self.id)
        self.assertIn(self.labelkey, subject.preds)
        clone = Subject(subject.id, predlist=subject.preds)
        # All values of 'clone' should match those of the copied 'subject'
        self.assertEqual(subject.id, clone.id)
        for predicate in subject.preds:
            self.assertEqual(subject.preds[predicate], clone.preds[predicate])
        miss = Subject(self.missing)
        # skmf:undefined should not be found in the triplestore, empty subject
        self.assertEqual(miss.id, self.missing)
        self.assertFalse(miss.preds)
        self.assertNotIn('miss', miss.graphs)
        miss.add_graphs({'miss'})
        # graph 'miss' should be in 'graphs' list
        self.assertIn('miss', miss.graphs)
        miss.remove_graphs({'miss'})
        # graph 'miss' should no longer be in 'graphs' list
        self.assertNotIn('miss', miss.graphs)
        miss.add_data(graphlist={''}, predlist=self.predlist)
        # data should appear in object
        self.assertIn(self.labelkey, miss.preds)
        self.assertIn(self.rdfobject, miss.preds[self.labelkey]['value'])
        clone = Subject(miss.id)
        # 'clone' should have pulled added data from triplestore
        self.assertIn(self.labelkey, clone.preds)
        self.assertIn(self.rdfobject, clone.preds[self.labelkey]['value'])
        miss.remove_data(graphlist={''}, predlist=self.predlist)
        # data should no longer appear in object
        self.assertNotIn(self.labelkey, miss.preds)
        clone = Subject(miss.id)
        # 'clone' should no longer pull removed data from triplestore
        self.assertNotIn(self.labelkey, clone.preds)


class ResourceUserTestCase(BaseTestCase):
    """Unit tests to verify correct behavior of SKMF Users and methods.
    
    Validate the behavior of User loading through SPARQL endpoint operations.
    """
    
    username = 'admin'
    hashpass = b'$2b$12$/t7tQAxpH1cfwIYk.guuIuhQF5GBtoHqaokpxIhsOJNiIng2i.IA.'
    realname = 'Administrator'
    graphlist = {'users'}

    def test_resource_user(self):
        """Verify that Users are properly loaded and defined."""
        user = User(self.username)
        self.assertIn(User.actkey, user.preds)
        self.assertIn(User.hashkey, user.preds)
        self.assertIn(User.namekey, user.preds)
        self.assertFalse(user.is_authenticated())
        self.assertTrue(user.is_active())
        self.assertFalse(user.is_anonymous())
        self.assertEqual(user.get_id(), self.username)
        self.assertEqual(user.get_hash(), self.hashpass)
        self.assertEqual(user.get_name(), self.realname)


class FlaskTestCase(BaseTestCase):
    """Unit tests to verify the correct behavior of Flask views and templates.
    
    Validate the behavior of template rendering, redirects, session management,
    form handling, error handling, and SPARQL endpoint operations.
    """

    def test_views_get_responses(self):
        """Verify that proper responses are returned from named views."""
        self.assert200(self.client.get(url_for('resources')))
        self.assertTemplateUsed('resources.html')
        self.assertContext('title', uiLabel.viewTagTitle)
        self.assert200(self.client.get(url_for('login')))
        self.assertTemplateUsed('login.html')
        self.assertContext('title', uiLabel.viewLoginTitle)
        self.assert405(self.client.get(url_for('add_tag')))
        response = self.client.get(url_for('add_user'))
        self.assertRedirects(response, url_for('login') + '?next=%2Fusers')

    def test_login_logout(self):
        """Verify that user sessions are initiated and torn down properly."""
        with self.client:
            self.assertTrue(current_user.is_anonymous)
            self.login('admin', 'default')
            self.assertEqual(current_user.get_id(), 'admin')
            self.assertTrue(
                self.bcrypt.check_password_hash(
                    current_user.get_hash(), 'default'))
            self.assertEqual(current_user.get_name(), 'Administrator')
            self.assertTrue(current_user.is_authenticated())
            self.assertTrue(current_user.is_active())
            self.assertFalse(current_user.is_anonymous())
            response = self.logout()
            self.assertTrue(current_user.is_anonymous)
            self.assertIn('You were logged out', response.data.decode('utf-8'))

    def test_login_invalid(self):
        """Verify that invalid credentials do not create a user session."""
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

    def test_view_restricted(self):
        """Verify view behavior when user is not logged in."""
        with self.client:
            response = self.client.post(url_for('add_tag'), data=dict(
                label='Label',
                description='A short description.'))
            self.assertRedirects(response, url_for('login') + '?next=%2Fadd')
        with self.client:
            response = self.client.post(url_for('add_user'), data=dict(
                username='bob',
                password='password',
                confirm='password'))
            self.assertRedirects(response, url_for('login') + '?next=%2Fusers')
            self.login('bob', 'default', True)
            self.assertTrue(current_user.is_anonymous)
            self.login('admin', 'default', True)
            self.assert200(self.client.get(url_for('add_user')))
            self.assertTemplateUsed('users.html')
            self.assertContext('title', uiLabel.viewUserTitle)

if __name__ == '__main__':
    unittest.main()
