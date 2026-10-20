"""Validação do JWT emitido pelo Supabase Auth.

O front envia:  Authorization: Bearer <access_token>

- Tokens HS256 (projetos com "JWT secret" legado): validados com SUPABASE_JWT_SECRET.
- Tokens RS256/ES256 (chaves assimétricas novas): validados via JWKS em SUPABASE_URL.
"""
import uuid
from functools import wraps

import jwt
from flask import current_app, g, jsonify, request
from jwt import PyJWKClient

_jwks_client = None


def _get_jwks_client():
    global _jwks_client
    if _jwks_client is None:
        base = current_app.config.get("SUPABASE_URL")
        if not base:
            raise jwt.InvalidTokenError("SUPABASE_URL não configurada (necessária para validar via JWKS)")
        _jwks_client = PyJWKClient(f"{base.rstrip('/')}/auth/v1/.well-known/jwks.json", cache_keys=True)
    return _jwks_client


def _decode_token(token):
    alg = jwt.get_unverified_header(token).get("alg")
    if alg == "HS256":
        secret = current_app.config.get("SUPABASE_JWT_SECRET")
        if not secret:
            raise jwt.InvalidTokenError("SUPABASE_JWT_SECRET não configurado")
        return jwt.decode(token, secret, algorithms=["HS256"], audience="authenticated")
    chave = _get_jwks_client().get_signing_key_from_jwt(token).key
    return jwt.decode(token, chave, algorithms=["RS256", "ES256"], audience="authenticated")


def _carregar_usuario():
    """Preenche g.user_id / g.claims. Retorna None se ok, ou um texto com o motivo da falha."""
    g.user_id = None
    g.claims = {}
    header = request.headers.get("Authorization", "")
    if not header.lower().startswith("bearer "):
        return "Token de acesso ausente"
    try:
        claims = _decode_token(header[7:].strip())
    except jwt.PyJWTError as e:
        current_app.logger.info("Token rejeitado: %s", e)
        return "Token inválido ou expirado"
    g.claims = claims
    g.user_id = claims.get("sub")
    return None


def auth_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        erro = _carregar_usuario()
        if erro:
            return jsonify(erro=erro, codigo=401), 401
        return f(*args, **kwargs)

    return wrapper


def optional_auth(f):
    """Identifica o usuário se houver token válido, mas não bloqueia visitantes."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        _carregar_usuario()
        return f(*args, **kwargs)

    return wrapper


def user_uuid():
    """UUID do usuário logado (ou None)."""
    uid = getattr(g, "user_id", None)
    try:
        return uuid.UUID(uid) if uid else None
    except ValueError:
        return None
