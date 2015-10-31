from flask import Flask

app = Flask(__name__.split('.')[0])
app.config.from_object('skmf.def_conf')
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
#from skmf import views
