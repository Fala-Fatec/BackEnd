import os

from dotenv import load_dotenv

load_dotenv()


def _lista(valor, padrao=""):
    return [v.strip() for v in os.getenv(valor, padrao).split(",") if v.strip()]


def _database_url():
    url = os.getenv("DATABASE_URL", "")
    # SQLAlchemy 2.x não aceita o prefixo antigo "postgres://"
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


class Config:
    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # pool_pre_ping evita erro com conexões que o pooler do Supabase derrubou
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 300}

    # Autenticação (tokens emitidos pelo Supabase Auth)
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")  # usado para validar via JWKS
    SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "")  # usado para tokens HS256

    # CORS: lista separada por vírgula. "*" libera qualquer origem (só para desenvolvimento)
    CORS_ORIGINS = _lista("CORS_ORIGINS", "*")

    # Se false, o nome do autor não é enviado ao front (feedbacks anônimos para o público)
    EXPOSE_AUTHOR = os.getenv("EXPOSE_AUTHOR", "true").lower() == "true"

    # Tipos de reação aceitos. Vazio = aceita qualquer texto.
    REACTION_TYPES = set(_lista("REACTION_TYPES", "like,dislike"))
