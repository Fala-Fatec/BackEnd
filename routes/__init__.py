from .categories import bp as categories_bp
from .feedbacks import bp as feedbacks_bp
from .me import bp as me_bp
from .reactions import bp as reactions_bp


def register_routes(app):
    for bp in (categories_bp, feedbacks_bp, reactions_bp, me_bp):
        app.register_blueprint(bp)
