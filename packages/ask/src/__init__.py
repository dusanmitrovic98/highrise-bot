from flask import Flask
from src.main.routes import main
from src.api.v1.routes import api_v1
from src.api.v2.routes import api_v2

def create_app():
    app = Flask(__name__)
    app.config.from_object('src.config.Config')

    app.register_blueprint(main)
    app.register_blueprint(api_v1, url_prefix='/api/v1')
    app.register_blueprint(api_v2, url_prefix='/api/v2')

    return app
