from flask import (
    Flask,
    request,
    render_template,
    url_for,
    redirect,
)
from collections import namedtuple

import sqlite3


dance = namedtuple("dance", ["id", "name", "url", "status"])

app = Flask(__name__)


@app.route("/")
def home():
    conn = sqlite3.connect("dance-progress.db")
    cur = conn.cursor()
    dances_list = cur.execute("select * from dance_progress order by name").fetchall()
    conn.close()
    dances = [dance(*x) for x in dances_list]
    return render_template("home.html", dances=dances)


@app.route("/set_status/", methods=["GET"])
def set_status():
    id = int(request.args["id"])
    status = int(request.args["status"])
    conn = sqlite3.connect("dance-progress.db")
    cur = conn.cursor()
    cur.execute("update dance_progress set status = ? where id = ?", (status, id))
    conn.commit()
    return redirect(url_for("home"))
