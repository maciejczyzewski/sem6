print("[APP]")

try:
    import IPython.core.ultratb
except ImportError:
    # No IPython. Use default exception printing.
    pass
else:
    import sys
    sys.excepthook = IPython.core.ultratb.ColorTB()

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import Config
from app.models import db

def create_app(config_class):
    app = Flask(__name__, static_url_path='',
            static_folder=os.path.abspath('static'))
    app.config.from_object(config_class)
    db.init_app(app)

    from app.routes_user import bp as routes_user_bp
    app.register_blueprint(routes_user_bp)

    from app.routes_tournament import bp as routes_tournament_bp
    app.register_blueprint(routes_tournament_bp)

    return app, db


class Service():
    app = None
    db = None

    def __init__(self, config=Config):
        self.app, self.db = create_app(config)
        self.app.service = self
        self.app_context = self.app.app_context()

    def start(self):
        self.app_context.push()
        self.db.create_all()

    def end(self):
        self.db.session.remove()
        self.db.drop_all()
        self.app_context.pop()
