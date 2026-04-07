from flask import Blueprint, request, jsonify
from hebergement_service import (
    get_all_hebergements,
    get_hebergement_by_id
)

api = Blueprint("api", __name__)

@api.route("/hebergements", methods=["GET"])
def hebergements():
    ville = request.args.get("ville")
    type_hebergement = request.args.get("type")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))

    data = get_all_hebergements(ville, type_hebergement, page, per_page)
    return jsonify(data)


@api.route("/hebergements/<int:id>", methods=["GET"])
def hebergement_detail(id):
    data = get_hebergement_by_id(id)

    if data:
        return jsonify(data)
    else:
        return jsonify({"error": "Not found"}), 404