from flask import Flask
from .config import Config
from .api.v1 import user_bp,auth_bp,dish_bp,order_bp
from .extensions import db
from .cli import init_app as init_cli
def create_app():
    
    # 创建 Flask 核心实例
    app = Flask(__name__)
    
    # 从 Config 这个类中加载所有的配置变量
    app.config.from_object(Config)
    
    # 将之前定义好的 db 扩展实例，绑定到当前创建的 app 实例上
    db.init_app(app)
    
    # 蓝图注册
    app.register_blueprint(user_bp, url_prefix='/api/v1/users')
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(dish_bp, url_prefix='/api/v1/dishes')
    app.register_blueprint(order_bp,url_prefix='api/v1/orders')
    
    init_cli(app)
    return app

    