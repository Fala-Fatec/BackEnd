"""Models que ESPELHAM as tabelas já existentes no Supabase (schema public).

Não use db.create_all(): o schema é gerenciado no Supabase.
"""
from sqlalchemy.dialects.postgresql import UUID

from extensions import db

UUID_PK = dict(primary_key=True, server_default=db.text("gen_random_uuid()"))


class Profile(db.Model):
    __tablename__ = "profiles"

    id = db.Column(UUID(as_uuid=True), primary_key=True)  # = auth.users.id
    nome = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    curso = db.Column(db.Text)
    semestre = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(timezone=True))
    updated_at = db.Column(db.DateTime(timezone=True))


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.Text, nullable=False, unique=True)
    slug = db.Column(db.Text, nullable=False, unique=True)
    icone = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True))


class Feedback(db.Model):
    __tablename__ = "feedbacks"

    id = db.Column(UUID(as_uuid=True), **UUID_PK)
    author_id = db.Column(UUID(as_uuid=True), db.ForeignKey("profiles.id"), nullable=False)
    titulo = db.Column(db.Text, nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    categoria = db.Column(db.Text)  # legado: preferir category_id
    semestre_aluno = db.Column(db.Integer)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    created_at = db.Column(db.DateTime(timezone=True))
    updated_at = db.Column(db.DateTime(timezone=True))

    author = db.relationship("Profile")
    category = db.relationship("Category")


class Reaction(db.Model):
    __tablename__ = "reactions"

    id = db.Column(db.BigInteger, primary_key=True)
    feedback_id = db.Column(UUID(as_uuid=True), db.ForeignKey("feedbacks.id"), nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("profiles.id"), nullable=False)
    type = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True))
