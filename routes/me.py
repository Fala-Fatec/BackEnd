from flask import Blueprint, abort, g, jsonify
from sqlalchemy import func

from auth import auth_required, user_uuid
from extensions import db
from models import Profile
from serializers import profile_private
from utils import clean_text, get_json_body, parse_int

bp = Blueprint("me", __name__, url_prefix="/api")


@bp.get("/me")
@auth_required
def meu_perfil():
    perfil = db.session.get(Profile, user_uuid())
    if perfil is None:
        abort(404, description="Perfil não encontrado. Crie-o com PUT /api/me.")
    return jsonify(profile_private(perfil)), 200


@bp.put("/me")
@auth_required
def salvar_perfil():
    """Cria o perfil (primeiro acesso) ou atualiza o existente.

    Corpo: {"nome": "...", "curso": "...", "semestre": 3}
    No primeiro acesso, "nome" é obrigatório; o e-mail vem do token.
    """
    dados = get_json_body()
    uid = user_uuid()
    perfil = db.session.get(Profile, uid)
    criado = perfil is None

    if criado:
        email = g.claims.get("email")
        if not email:
            abort(400, description="O token não contém e-mail; não foi possível criar o perfil")
        perfil = Profile(id=uid, email=email, nome=clean_text(dados.get("nome"), "nome", 120))
        db.session.add(perfil)
    elif "nome" in dados:
        perfil.nome = clean_text(dados["nome"], "nome", 120)

    if "curso" in dados:
        perfil.curso = clean_text(dados["curso"], "curso", 120, required=False)
    if "semestre" in dados:
        perfil.semestre = parse_int(dados["semestre"], "semestre", 1, 12, required=False)

    perfil.updated_at = func.now()
    db.session.commit()
    return jsonify(profile_private(perfil)), (201 if criado else 200)
