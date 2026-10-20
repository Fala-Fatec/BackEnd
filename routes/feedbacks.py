from flask import Blueprint, abort, jsonify, request
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from auth import auth_required, optional_auth, user_uuid
from extensions import db
from models import Category, Feedback, Profile, Reaction
from serializers import feedback_to_dict
from services import reacoes_por_feedback
from utils import clean_text, get_json_body, paginacao_args, parse_int

bp = Blueprint("feedbacks", __name__, url_prefix="/api")


def _query_base():
    return Feedback.query.options(joinedload(Feedback.author), joinedload(Feedback.category))


def _serializar(feedback, uid):
    contagens, minhas = reacoes_por_feedback([feedback.id], uid)
    return feedback_to_dict(feedback, contagens.get(feedback.id), minhas.get(feedback.id), uid)


def _listar(q, uid):
    page, per_page = paginacao_args()
    pag = q.paginate(page=page, per_page=per_page, error_out=False)
    contagens, minhas = reacoes_por_feedback([f.id for f in pag.items], uid)
    return jsonify(
        items=[feedback_to_dict(f, contagens.get(f.id), minhas.get(f.id), uid) for f in pag.items],
        page=pag.page,
        per_page=per_page,
        pages=pag.pages,
        total=pag.total,
    )


def _resolver_categoria(valor):
    if valor is None:
        return None
    categoria = db.session.get(Category, parse_int(valor, "category_id"))
    if categoria is None:
        abort(400, description="category_id não existe")
    return categoria


def _exigir_autor(feedback, acao):
    if feedback.author_id != user_uuid():
        abort(403, description=f"Apenas o autor pode {acao} este feedback")


# ---------------------------------------------------------------- listagem
@bp.get("/feedbacks")
@optional_auth
def listar_feedbacks():
    q = _query_base()

    if slug := request.args.get("category"):
        q = q.filter(Feedback.category.has(slug=slug))
    if cat_id := request.args.get("category_id", type=int):
        q = q.filter(Feedback.category_id == cat_id)
    if semestre := request.args.get("semestre", type=int):
        q = q.filter(Feedback.semestre_aluno == semestre)
    if busca := (request.args.get("q") or "").strip():
        termo = f"%{busca}%"
        q = q.filter(Feedback.titulo.ilike(termo) | Feedback.conteudo.ilike(termo))

    ordem = request.args.get("ordem", "recentes")
    if ordem == "antigos":
        q = q.order_by(Feedback.created_at.asc().nullslast())
    elif ordem == "populares":
        total = (
            db.session.query(Reaction.feedback_id.label("fid"), func.count(Reaction.id).label("n"))
            .group_by(Reaction.feedback_id)
            .subquery()
        )
        q = q.outerjoin(total, total.c.fid == Feedback.id).order_by(
            func.coalesce(total.c.n, 0).desc(), Feedback.created_at.desc().nullslast()
        )
    else:
        q = q.order_by(Feedback.created_at.desc().nullslast())

    return _listar(q, user_uuid())


@bp.get("/me/feedbacks")
@auth_required
def meus_feedbacks():
    uid = user_uuid()
    q = _query_base().filter(Feedback.author_id == uid).order_by(Feedback.created_at.desc().nullslast())
    return _listar(q, uid)


@bp.get("/feedbacks/<uuid:feedback_id>")
@optional_auth
def obter_feedback(feedback_id):
    feedback = _query_base().filter(Feedback.id == feedback_id).first_or_404(
        description="Feedback não encontrado"
    )
    return jsonify(_serializar(feedback, user_uuid())), 200


# ---------------------------------------------------------------- escrita
@bp.post("/feedbacks")
@auth_required
def criar_feedback():
    dados = get_json_body()
    uid = user_uuid()

    perfil = db.session.get(Profile, uid)
    if perfil is None:
        abort(409, description="Perfil não encontrado. Complete o cadastro em PUT /api/me antes de publicar.")

    titulo = clean_text(dados.get("titulo"), "titulo", 200)
    conteudo = clean_text(dados.get("conteudo"), "conteudo", 5000)
    categoria = _resolver_categoria(dados.get("category_id"))
    semestre = parse_int(dados.get("semestre_aluno"), "semestre_aluno", 1, 12, required=False)
    if semestre is None:
        semestre = perfil.semestre

    feedback = Feedback(
        author_id=uid,
        titulo=titulo,
        conteudo=conteudo,
        category_id=categoria.id if categoria else None,
        categoria=categoria.nome if categoria else None,  # mantém a coluna legada coerente
        semestre_aluno=semestre,
    )
    db.session.add(feedback)
    db.session.commit()
    return jsonify(_serializar(feedback, uid)), 201


@bp.route("/feedbacks/<uuid:feedback_id>", methods=["PUT", "PATCH"])
@auth_required
def atualizar_feedback(feedback_id):
    feedback = db.get_or_404(Feedback, feedback_id, description="Feedback não encontrado")
    _exigir_autor(feedback, "editar")
    dados = get_json_body()

    if "titulo" in dados:
        feedback.titulo = clean_text(dados["titulo"], "titulo", 200)
    if "conteudo" in dados:
        feedback.conteudo = clean_text(dados["conteudo"], "conteudo", 5000)
    if "category_id" in dados:
        categoria = _resolver_categoria(dados["category_id"])
        feedback.category_id = categoria.id if categoria else None
        feedback.categoria = categoria.nome if categoria else None
    if "semestre_aluno" in dados:
        feedback.semestre_aluno = parse_int(dados["semestre_aluno"], "semestre_aluno", 1, 12, required=False)

    feedback.updated_at = func.now()
    db.session.commit()
    return jsonify(_serializar(feedback, user_uuid())), 200


@bp.delete("/feedbacks/<uuid:feedback_id>")
@auth_required
def deletar_feedback(feedback_id):
    feedback = db.get_or_404(Feedback, feedback_id, description="Feedback não encontrado")
    _exigir_autor(feedback, "excluir")

    Reaction.query.filter_by(feedback_id=feedback_id).delete()
    db.session.delete(feedback)
    db.session.commit()
    return jsonify(mensagem="Feedback excluído com sucesso"), 200
