from flask import (
    Flask,
    Blueprint,
    request,
    render_template,
    url_for,
    redirect,
    session,
    send_from_directory,
)


from collections import namedtuple
import os

import psycopg

EXPECTED_KEYS = [
    "PGPASSWORD",
    "POSTGRES_HOST",
    "POSTGRES_USER",
]
assert all([x in os.environ for x in EXPECTED_KEYS]), set(EXPECTED_KEYS) - set(
    os.environ.keys()
)


dance = namedtuple("dance", ["id", "name", "keywords", "url", "status", "interest"])

STORAGE_DIR = os.environ["STORAGE_DIR"]

app = Flask(__name__)
app.secret_key = (
    "my super secret keyhwuqbwefjhcuapjebqawihw"  # TODO move this somewhere else
)
bp = Blueprint("linedance-tracker", __name__, url_prefix="/linedance-tracker")


def plural(x: str, n: int) -> str:
    """
    Returns plural? form of x
    """
    return x if n == 1 else x + "s"


app.jinja_env.filters["plural"] = plural


@bp.route("/static/<filename>")
def static(filename: str):
    return send_from_directory("static", filename)


@bp.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        username = request.form["username"].lower()
        if username:
            session["username"] = username
        return redirect(url_for("linedance-tracker.home"))
    conn = psycopg.connect(
        host=os.environ["POSTGRES_HOST"], user=os.environ["POSTGRES_USER"]
    )
    cur = conn.cursor()
    username = session.get("username")
    params = {
        "username": username,
    }
    dances_list = cur.execute(
        """
with t1 as (
    with t0 as (
        select dances.id, dances.name, dances.keywords, dances.url, progress.status
        , %(username)s as username
        from dances
        left join progress
        on dances.id = progress.id
        and progress.username = %(username)s
    )
    select id, name, keywords, url, username,
    case when status is null then 0 else status end as status
    from t0
)
select t1.id, t1.name, t1.keywords, t1.url, t1.status
,case when interest.interest is null then 0 else interest.interest end as interest
from t1
left join interest
on t1.id = interest.id
and t1.username = interest.username
order by interest desc, status desc, name asc
""",
        params,
    ).fetchall()
    conn.close()
    dances = [dance(*x) for x in dances_list]
    return render_template("home.html", dances=dances, username=username)


@bp.route("/logout")
def logout():
    del session["username"]
    return redirect(url_for("linedance-tracker.home"))


@bp.route("/toggle_interest", methods=["GET"])
def toggle_interest():
    id_n = int(request.args["id"])
    conn = psycopg.connect(
        host=os.environ["POSTGRES_HOST"], user=os.environ["POSTGRES_USER"]
    )
    cur = conn.cursor()
    username = session["username"]
    interest_tuple = cur.execute(
        "select interest from interest where id = %s and username = %s",
        (id_n, username),
    ).fetchone()
    if interest_tuple is None:
        query = """
                    insert into interest (username, id, interest) values (%(username)s, %(id)s, 1)
                    """
        new_interest = -1  # unused
    else:
        current_interest = interest_tuple[0]
        new_interest = 1 - current_interest
        query = """
                    update interest set interest = %(new_interest)s
                    where username = %(username)s and id = %(id)s
                    """
    params = {
        "username": username,
        "id": id_n,
        "new_interest": new_interest,
    }
    cur.execute(query, params)
    conn.commit()
    conn.close()
    return redirect(url_for("linedance-tracker.home"))


@bp.route("/increment/", methods=["GET"])
def set_status():
    id_n = int(request.args["id"])
    conn = psycopg.connect(
        host=os.environ["POSTGRES_HOST"], user=os.environ["POSTGRES_USER"]
    )
    cur = conn.cursor()
    username = session["username"]
    status_tuple = cur.execute(
        "select status from progress where id = %s and username = %s", (id_n, username)
    ).fetchone()
    if status_tuple is None:
        new_status = 1
        query = """
                    insert into progress (username, id, status)
                    values (%(username)s, %(id)s, %(new_status)s)
                    """
    else:
        new_status = (status_tuple[0] + 1) % 2
        query = """
                    update progress set status = %(new_status)s
                    where username = %(username)s and id = %(id)s
                    """
    params = {
        "new_status": new_status,
        "username": username,
        "id": id_n,
    }
    cur.execute(query, params)
    conn.commit()
    conn.close()
    return redirect(url_for("linedance-tracker.home"))


@app.errorhandler(404)
def page_not_found(e):
    return "404 error", 404


app.register_blueprint(bp)
