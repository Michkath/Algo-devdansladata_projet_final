from flask import Blueprint, request, jsonify
from hebergement_service import get_all_hebergements, get_hebergement_by_id

# Création du Blueprint
api = Blueprint("api", __name__)

@api.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "message": "pong"})

@api.route("/hebergements", methods=["GET"])
def hebergements():
    ville = request.args.get("ville", "").strip()
    type_h = request.args.get("type", "").strip()
    classement = request.args.get("classement", "").strip()
    page = max(1, int(request.args.get("page", 1)))
    per_page = max(1, min(100, int(request.args.get("per_page", 20))))

    results, total = get_all_hebergements(ville, type_h, classement, page, per_page)
    
    data = {
        "page": page,
        "per_page": per_page,
        "total": total,
        "hebergements": results
    }

    return jsonify(data)

@api.route("/hebergements/<int:id>", methods=["GET"])
def hebergement_detail(id):
    data = get_hebergement_by_id(id)

    if data:
        return jsonify(data)
    else:
        return jsonify({"error": "Hébergement non trouvé"}), 404