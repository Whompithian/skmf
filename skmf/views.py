from skmf import app

class View(object):

    @app.route('/')
    @app.route('/index')
    def index(self):
        return "Hello, World!"
