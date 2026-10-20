from flask import jsonify
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.exceptions import HTTPException

from extensions import db


def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def http_error(e):
        return jsonify(erro=e.description, codigo=e.code), e.code

    @app.errorhandler(IntegrityError)
    def integrity_error(e):
        db.session.rollback()
        app.logger.warning("IntegrityError: %s", e.orig)
        return jsonify(erro="Conflito com dados existentes ou referência inválida", codigo=409), 409

    @app.errorhandler(SQLAlchemyError)
    def db_error(e):
        db.session.rollback()
        app.logger.exception("Erro de banco de dados")
        return jsonify(erro="Erro ao acessar o banco de dados", codigo=500), 500

    @app.errorhandler(Exception)
    def unexpected_error(e):
        app.logger.exception("Erro inesperado")
        return jsonify(erro="Erro interno do servidor", codigo=500), 500
