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
        if request.form["username"]:
            session["username"] = request.form["username"]
        return redirect(url_for("home"))
    conn = sqlite3.connect(os.path.join(STORAGE_DIR, "dance-progress.db"))
    cur = conn.cursor()
    username = session.get("username")
    user_filter = (
        f"""and progress.username = '{username}'"""
        if username is not None
        else "and 1 = 2"  # return no progress if not logged in
    )
    dances_list = cur.execute(
        f"""with t0 as (
    select dances.id, dances.name, dances.url, progress.status
    from dances
    left join progress
    on dances.id = progress.id
    {user_filter}
)
select id, name, url, case when status is null then 0 else status end
from t0
order by status desc, name asc"""
    ).fetchall()
    conn.close()
    dances = [dance(*x) for x in dances_list]
    return render_template("home.html", dances=dances, username=session.get("username"))


@app.route("/logout")
def logout():
    del session["username"]
    return redirect(url_for("home"))


@app.route("/increment/", methods=["GET"])
def set_status():
    id = int(request.args["id"])
    conn = sqlite3.connect(os.path.join(STORAGE_DIR, "dance-progress.db"))
    cur = conn.cursor()
    username = session["username"]
    status_obj = cur.execute(
        "select status from progress where id = ? and username = ?", (id, username)
    ).fetchone()
    if status_obj is None:
        new_status = 1
        query = f"""
                    insert into progress (username, id, status) values ('{username}', {id}, {new_status})
                    """
    else:
        new_status = (status_obj[0] + 1) % 3
        query = f"""
                    update progress set status = {new_status}
                    where username = '{username}' and id = '{id}'
                    """
    cur.execute(query)
    conn.commit()
    conn.close()
    return redirect(url_for("home"))
