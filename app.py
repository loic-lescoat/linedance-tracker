from flask import (
    Flask,
    request,
    render_template,
    send_file,
    send_from_directory,
)
from collections import namedtuple

import sqlite3


dance = namedtuple("dance", ["name", "url", "status"])

app = Flask(__name__)


@app.route("/")
def home():
    conn = sqlite3.connect("dance-progress.db")
    cur = conn.cursor()
    dances_list = cur.execute(
        "select name, url, status from dance_progress order by name"
    ).fetchall()
    conn.close()
    dances = [dance(*x) for x in dances_list]
    return render_template("home.html", dances=dances)
