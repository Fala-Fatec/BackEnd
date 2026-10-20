from flask import current_app


def _iso(dt):
    return dt.isoformat() if dt else None


def category_to_dict(c, total_feedbacks=None):
    d = {"id": c.id, "nome": c.nome, "slug": c.slug, "icone": c.icone}
    if total_feedbacks is not None:
        d["total_feedbacks"] = total_feedbacks
    return d


def profile_public(p):
    """Dados do autor exibidos publicamente (sem e-mail)."""
    return {"id": str(p.id), "nome": p.nome, "curso": p.curso, "semestre": p.semestre}


def profile_private(p):
    """Perfil completo, apenas para o próprio usuário (GET/PUT /api/me)."""
    return {
        "id": str(p.id),
        "nome": p.nome,
        "email": p.email,
        "curso": p.curso,
        "semestre": p.semestre,
        "created_at": _iso(p.created_at),
        "updated_at": _iso(p.updated_at),
    }


def feedback_to_dict(f, reacoes=None, minha_reacao=None, uid=None):
    expor_autor = current_app.config["EXPOSE_AUTHOR"]
    reacoes = reacoes or {}
    return {
        "id": str(f.id),
        "titulo": f.titulo,
        "conteudo": f.conteudo,
        "categoria": f.category.nome if f.category else f.categoria,
        "category": category_to_dict(f.category) if f.category else None,
        "semestre_aluno": f.semestre_aluno,
        "autor": profile_public(f.author) if (expor_autor and f.author) else None,
        "eh_autor": uid is not None and f.author_id == uid,
        "reacoes": reacoes,
        "total_reacoes": sum(reacoes.values()),
        "minha_reacao": minha_reacao,
        "created_at": _iso(f.created_at),
        "updated_at": _iso(f.updated_at),
    }
