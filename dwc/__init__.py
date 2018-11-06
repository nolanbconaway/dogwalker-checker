from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import datetime
import os
app = Flask(__name__)

# set up database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']
db = SQLAlchemy(app)

# set up limiter
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)


def sql(query):
    """Run a query, return the results."""
    result = db.engine.execute(query)
    cols = result.keys()
    return [dict(zip(cols, i)) for i in result.fetchall()]


@app.context_processor
def inject_data():
    """Inject some helpful data into the template."""
    return dict(
        weekday=datetime.date.today().weekday()
    )


def delta2time(delta):
    """Convert a timedelta to a time object."""
    return (datetime.datetime.min + delta).time()


@app.route("/")
@limiter.limit("8 per minute")
def index():
    """Return the index page."""
    rows = sql('''SELECT * from histogram''')

    today = sql('''
        SELECT tm, walker, note
        FROM walks
        WHERE dt = DATE(DATE_SUB(NOW(), INTERVAL 4 HOUR)) # utc to eastern
        ORDER BY dttm DESC
        LIMIT 1
    ''')
    today = None if not today else today[0]

    return render_template(
        'hist.html',
        x=[delta2time(i['tm']).strftime('%H:%M') for i in rows],
        y=[i['n'] for i in rows],
        today=today,
    )
