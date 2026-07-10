from flask import Flask
from .config import Config
from .api.v1 import user_bp,auth_bp,dish_bp,order_bp
from .extensions import db
from .cli import init_app as init_cli
from flask_cors import CORS
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    
    # 创建 Flask 核心实例
    app = Flask(__name__)
    CORS(app)
    # 从 Config 这个类中加载所有的配置变量
    app.config.from_object(Config)
    
    # 将之前定义好的 db 扩展实例，绑定到当前创建的 app 实例上
    db.init_app(app)
    
    # 蓝图注册
    app.register_blueprint(user_bp, url_prefix='/api/v1/users')
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(dish_bp, url_prefix='/api/v1/dishes')
    app.register_blueprint(order_bp,url_prefix='/api/v1/orders')
    
    init_cli(app)
     # ---------- 全局错误处理 ----------
    @app.errorhandler(400)
    def bad_request(error):
        return {"error": "请求格式错误", "message": str(error.description)}, 400

    @app.errorhandler(404)
    def not_found(error):
        return {"error": "请求资源不存在"}, 404

    @app.errorhandler(500)
    def internal_error(error):
        # 生产环境不要暴露异常细节，但记录日志
        logger.error(f"服务器内部错误: {error}")
        return {"error": "服务器内部错误，请稍后重试"}, 500

    @app.errorhandler(Exception)
    def handle_all_exceptions(error):
        # 捕获所有未处理的异常，确保返回统一格式
        logger.error(f"未捕获的异常: {error}")
        return {"error": "服务器内部错误，请稍后重试"}, 500
    
    return app

    