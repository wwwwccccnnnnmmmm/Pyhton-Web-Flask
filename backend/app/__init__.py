from flask import Flask
from .config import Config
from .api.v1 import user_bp,auth_bp

def create_app():
    
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 蓝图注册
    app.register_blueprint(user_bp, url_prefix='/api/v1')
    app.register_blueprint(auth_bp, url_prefix='/api/v1')
    
    return app

    