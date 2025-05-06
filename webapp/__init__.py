from flask import Flask
from flask_cors import CORS

cors = CORS()

def create_app():
    app = Flask(__name__)
    cors.init_app(app)
    # Register blueprints or routes here
    from .routes import routes
    app.register_blueprint(routes, url_prefix='/')
    app.config["SECRET_KEY"]="test"
    return app