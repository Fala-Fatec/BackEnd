from flask import Blueprint, jsonify
from sqlalchemy import func

from extensions import db
from models import Category, Feedback
from serializers import category_to_dict

bp = Blueprint("categories", __name__, url_prefix="/api")


@bp.get("/categories")
def listar_categorias():
    linhas = (
        db.session.query(Category, func.count(Feedback.id))
        .outerjoin(Feedback, Feedback.category_id == Category.id)
        .group_by(Category.id)
        .order_by(Category.nome)
        .all()
    )
    return jsonify([category_to_dict(c, total) for c, total in linhas]), 200
