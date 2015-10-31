import os
import run
import skmf
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):

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
        run.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(skmf.app.config['DATABASE'])

    def test_empty_db(self):
        rv = self.app.get('/')
        self.assertIn('No entries here so far', rv.data)

    def test_login_logout(self):
        rv = self.login('admin', 'default')
        self.assertIn('You were logged in', rv.data)
        rv = self.logout()
        self.assertIn('You were logged out', rv.data)
        rv = self.login('adminx', 'default')
        self.assertIn('Invalid username', rv.data)
        rv = self.login('admin', 'defaultx')
        self.assertIn('Invalid password', rv.data)

    def test_messages(self):
        self.login('admin', 'default')
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here'
        ), follow_redirects=True)
        self.assertNotIn('No entries here so far', rv.data)
        self.assertIn('&lt;Hello&gt;', rv.data)
        self.assertIn('<strong>HTML</strong> allowed here', rv.data)

    with skmf.app.test_request_context('/?name=Peter'):
        self.assertEqual(flask.request.path, '/')
        self.assertEqual(flask.request.args['name'], 'Peter')

if __name__ == '__main__':
    unittest.main()
