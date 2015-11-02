"""skmf.def_conf by Brendan Sweeney, CSS 593, 2015.

Set of default configuration values for the Flask component. These values are
placed in a separate file for maintainability and this default file may be
overridden by specifying a different file with the FLASKR_SETTINGS environment
variable. This will prevent settings from being overwritten by the defaults in
the event of a package upgrade.
"""

#: Full path to the database file to be created by init_db()
DATABASE = '/tmp/flaskr.db'
#: Set Flask to run in degug mode (True) or production mode (False)
DEBUG = True
#: Set Flask to run in test mode (True) or normal mode (False)
TESTING = False
#: Synchronizer token to mitigate cross-site request forgery during development
SECRET_KEY = '`x8/5~Lt{|;"yHEpQW;E&0D"Zd=OdlaqF)Q}|ikI-ohAdj_m`,U~pdC$$?-3=vsn'
#: Username for running unit tests
USERNAME = 'admin'
#: Password for running unit tests
PASSWORD = 'default'
