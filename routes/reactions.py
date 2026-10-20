from flask import Blueprint, abort, current_app, jsonify

from auth import auth_required, user_uuid
from extensions import db
from models import Feedback, Profile, Reaction
from services import reacoes_por_feedback
from utils import clean_text, get_json_body

bp = Blueprint("reactions", __name__, url_prefix="/api")


def _resposta(acao, feedback_id, uid):
    contagens, minhas = reacoes_por_feedback([feedback_id], uid)
    return jsonify(
        acao=acao,
        reacoes=contagens.get(feedback_id, {}),
        minha_reacao=minhas.get(feedback_id),
    )


@bp.post("/feedbacks/<uuid:feedback_id>/reactions")
@auth_required
def reagir(feedback_id):
    """Alterna a reação do usuário.

    - sem reação anterior   -> cria
    - mesma reação já feita -> remove
    - outra reação          -> troca o tipo
    Corpo: {"type": "like"}
    """
    dados = get_json_body()
    tipo = clean_text(dados.get("type") or dados.get("tipo"), "type", 30)

    permitidos = current_app.config["REACTION_TYPES"]
    if permitidos and tipo not in permitidos:
        abort(400, description=f"Tipo de reação inválido. Use um destes: {', '.join(sorted(permitidos))}")

    db.get_or_404(Feedback, feedback_id, description="Feedback não encontrado")
    uid = user_uuid()
    if db.session.get(Profile, uid) is None:
        abort(409, description="Perfil não encontrado. Complete o cadastro em PUT /api/me antes de reagir.")

    existentes = (
        Reaction.query.filter_by(feedback_id=feedback_id, user_id=uid).order_by(Reaction.id).all()
    )

    if not existentes:
        db.session.add(Reaction(feedback_id=feedback_id, user_id=uid, type=tipo))
        acao = "criada"
    elif any(r.type == tipo for r in existentes):
        for r in existentes:
            db.session.delete(r)
        acao = "removida"
    else:
        existentes[0].type = tipo
        for r in existentes[1:]:  # limpa duplicatas antigas, se houver
            db.session.delete(r)
        acao = "trocada"

    db.session.commit()
    return _resposta(acao, feedback_id, uid), 200


@bp.delete("/feedbacks/<uuid:feedback_id>/reactions")
@auth_required
def remover_reacao(feedback_id):
    db.get_or_404(Feedback, feedback_id, description="Feedback não encontrado")
    uid = user_uuid()
    Reaction.query.filter_by(feedback_id=feedback_id, user_id=uid).delete()
    db.session.commit()
    return _resposta("removida", feedback_id, uid), 200
