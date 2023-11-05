from flask import Blueprint
from flask import request
from flask import jsonify
from be.model.search import Search

bp_search = Blueprint("search", __name__)

@bp_search.route("/search", methods=["POST"])
def search():
    # parse json body
    parameters = request.json.get("parameters")
    page = request.json.get("page")
    result_per_page = request.json.get("result_per_page")
    s = Search()
    code, message, results = s.search(parameters, page, result_per_page)
    return jsonify({"message": message, "results": results}), code