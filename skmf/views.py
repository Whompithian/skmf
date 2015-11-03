"""skmf.views by Armin Ronacher
(Modified by Brendan Sweeney, CSS 593, 2015.)

Currently, this is taken from the Flaskr tutorial and will need to be modified
as the frontend of the system is developed.
"""

from flask import render_template, request, session, redirect, url_for, \
                  abort, flash

from skmf import app, g


@app.route('/')
@app.route('/index')
def show_entries():
    cur = g.db.execute('select title, text from entries order by id desc')
    entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries, title='Flaskr')


@app.route('/tags', methods=['GET', 'POST'])
def show_tags():
    """Use results from a user to add a tag entry to the triplestore"""
    if request.method == 'POST':
        label = request.form['label']
        desc = request.form['description']
        subject = ''.join(c for c in label if c.isalnum()).rstrip()
        queryString = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX skmf: NAMESPACE
        INSERT DATA {
          skmf:SUBJECT rdfs:label "LABEL"@en-US ;
                       rdfs:comment "DESC"@en-US .
        }
        """
        queryString = queryString.replace('NAMESPACE', app.config['NAMESPACE'])
        queryString = queryString.replace('SUBJECT', subject)
        queryString = queryString.replace('LABEL', label)
        queryString = queryString.replace('DESC', desc)
        g.update.setQuery(queryString)
        try:
            g.update.query()
        except Exception as e:
            flash(str(e))
    queryString = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skmf: NAMESPACE
    SELECT DISTINCT ?label ?description
    WHERE {
      ?s rdfs:label ?label ;
         rdfs:comment ?description .
    }
    """
    queryString = queryString.replace('NAMESPACE', app.config['NAMESPACE'])
    g.sparql.setQuery(queryString)
    try:
        results = g.sparql.query().convert()
        return render_template('show_tags.html', title='Manage Tags', entries=results)
    except Exception as e:
        flash(str(e))
    return render_template('show_tags.html', title='Manage Tags')


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error, title='Login')


@app.route('/logout')
def logout():
    # The following line removes the session key, only if it exists
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404
