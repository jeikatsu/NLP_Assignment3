#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request
# from flask.ext.sqlalchemy import SQLAlchemy
import logging
import spacy
import re
import itertools

from spacy.matcher import Matcher
from spacy.util import filter_spans
from logging import Formatter, FileHandler
from forms import *
import os

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
#db = SQLAlchemy(app)

# Automatically tear down SQLAlchemy.
'''
@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()
'''

# Login required decorator.
'''
def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap
'''
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def home():
    with open('konosuba_chapter_1.txt', 'r', encoding="utf8") as f:
        text = f.read()
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)

    noun_span = list(doc.noun_chunks)


    pattern = [[{'POS': 'VERB'}, {'POS': 'ADV'}],
            [{'POS': 'ADV'}, {'POS': 'VERB'}],
            [{'POS': 'VERB'}]]
            
    matcher = Matcher(nlp.vocab)
    matcher.add("Verb phrase", pattern)
    matches = matcher(doc)
    spans = [doc[start:end] for _, start, end in matches]
    verb_span = filter_spans(spans)

    
    noun_phrases = []
    for n in noun_span:
        noun_phrases.append(str(n))

    verb_phrases = []
    for v in verb_span:
        verb_phrases.append(str(v))

    content = []
    text = " " + text 
    while  len(verb_phrases) and len(noun_phrases):
        n = text.find(noun_phrases[0])
        v = text.find(verb_phrases[0])

        if n < v:
            content.append((text[0: n], 'c'))
            content.append((noun_phrases[0], 'n'))
            text = text[n+len(noun_phrases[0]):len(text)]
            noun_phrases.pop(0)
        else:
            content.append((text[0: v], 'c'))
            content.append((verb_phrases[0], 'v'))
            text = text[v+len(verb_phrases[0]):len(text)]
            verb_phrases.pop(0)


    return render_template('pages/placeholder.home.html', content=content)


@app.route('/about')
def about():
    return render_template('pages/placeholder.about.html')


@app.route('/login')
def login():
    form = LoginForm(request.form)
    return render_template('forms/login.html', form=form)


@app.route('/register')
def register():
    form = RegisterForm(request.form)
    return render_template('forms/register.html', form=form)


@app.route('/forgot')
def forgot():
    form = ForgotForm(request.form)
    return render_template('forms/forgot.html', form=form)



# Error handlers.


@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
