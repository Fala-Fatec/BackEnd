from sqlalchemy import func

from extensions import db
from models import Reaction


def reacoes_por_feedback(ids, uid=None):
    """Retorna ({feedback_id: {tipo: total}}, {feedback_id: tipo_da_reacao_do_usuario})."""
    if not ids:
        return {}, {}

    linhas = (
        db.session.query(Reaction.feedback_id, Reaction.type, func.count(Reaction.id))
        .filter(Reaction.feedback_id.in_(ids))
        .group_by(Reaction.feedback_id, Reaction.type)
        .all()
    )
    contagens = {}
    for fid, tipo, total in linhas:
        contagens.setdefault(fid, {})[tipo] = total

    minhas = {}
    if uid is not None:
        for fid, tipo in db.session.query(Reaction.feedback_id, Reaction.type).filter(
            Reaction.feedback_id.in_(ids), Reaction.user_id == uid
        ):
            minhas[fid] = tipo
    return contagens, minhas
