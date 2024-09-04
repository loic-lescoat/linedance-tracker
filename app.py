from flask import (
    Flask,
    request,
    render_template,
    url_for,
    redirect,
    session,
)
from collections import namedtuple
import os

import sqlite3


dance = namedtuple("dance", ["id", "name", "url", "status"])

STORAGE_DIR = os.environ["STORAGE_DIR"]

app = Flask(__name__)
app.secret_key = (
    "my super secret keyhwuqbwefjhcuapjebqawihw"  # TODO move this somewhere else
)


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        session["username"] = request.form["username"]
        return redirect(url_for("home"))
    conn = sqlite3.connect(os.path.join(STORAGE_DIR, "dance-progress.db"))
    cur = conn.cursor()
    dances_list = cur.execute(
        "select * from dance_progress order by status desc, name asc"
    ).fetchall()
    conn.close()
    dances = [dance(*x) for x in dances_list]
    return render_template("home.html", dances=dances, username=session.get("username"))


@app.route("/increment/", methods=["GET"])
def set_status():
    id = int(request.args["id"])
    conn = sqlite3.connect(os.path.join(STORAGE_DIR, "dance-progress.db"))
    cur = conn.cursor()
    status = int(
        cur.execute("select status from dance_progress where id = ?", (id,)).fetchone()[
            0
        ]
    )
    cur.execute(
        "update dance_progress set status = ? where id = ?", ((status + 1) % 3, id)
    )
    conn.commit()
    conn.close()
    return redirect(url_for("home"))
