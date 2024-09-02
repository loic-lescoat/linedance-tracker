from flask import (
    Flask,
    request,
    render_template,
    send_file,
    send_from_directory,
)
from collections import namedtuple

dance = namedtuple("dance", ["name", "status"])

app = Flask(__name__)


@app.route("/")
def home():
    dances = [
            dance("hihi", 3),
            dance("hihi", 3),
            ]
    return render_template("home.html", dances=dances)
