from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # Register blueprints or routes here
    from .routes import routes
    app.register_blueprint(routes, url_prefix='/')
    app.config["SECRET_KEY"]="test"
    return app