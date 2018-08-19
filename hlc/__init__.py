from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy

import os

app = Flask(__name__)

# set up database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']
db = SQLAlchemy(app)


def sql(query):
    """Run a query, return the results."""
    result = db.engine.execute(query)
    cols = result.keys()
    return [dict(zip(cols, i)) for i in result.fetchall()]


@app.route("/")
def index():

    rows = sql('''
        SELECT t.tm, COUNT(w.id) AS n
        FROM `times` t LEFT JOIN `walks` w ON w.tm=t.tm
        GROUP BY t.tm ORDER BY 1
    ''')

    today = sql('''
        SELECT tm, walker, note
        FROM walks
        WHERE dt = CURDATE()
        -- WHERE dt = '2018-08-16'
        LIMIT 1
    ''')
    today = None if not today else today[0]

    return render_template(
        'hist.html',
        x=[str(i['tm']) for i in rows],
        y=[i['n'] for i in rows],
        today=today
    )
