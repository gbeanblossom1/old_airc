from flask import Blueprint
from flask import request
from flask import jsonify
from flask import Response
from flask import redirect
from flask import url_for
from flask import render_template


bp = Blueprint('views', __name__, url_prefix="/views")


@bp.route('/search', methods=("GET",))
def view_search():
    return render_template("search.html", url_root="http://localhost:5000")
