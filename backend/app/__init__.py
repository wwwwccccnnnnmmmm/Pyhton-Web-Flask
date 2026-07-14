from flask import Flask,request
from .config import Config
from .api.v1 import user_bp,auth_bp,dish_bp,order_bp
from .extensions import db,migrate
from .cli import init_app as init_cli
from flask_cors import CORS
import logging
from pathlib import Path


def create_app():
    
    # 创建 Flask 核心实例
    app = Flask(__name__)
    CORS(app)
    # 从 Config 这个类中加载所有的配置变量
    app.config.from_object(Config)
    
    # 将之前定义好的 db 扩展实例，绑定到当前创建的 app 实例上
    db.init_app(app)
    
    #绑定数据库和应用
    migrate.init_app(app,db)
    
    # 蓝图注册
    app.register_blueprint(user_bp, url_prefix='/api/v1/users')
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(dish_bp, url_prefix='/api/v1/dishes')
    app.register_blueprint(order_bp,url_prefix='/api/v1/orders')
    
    init_cli(app)
    
    base_dir = Path(app.root_path).parent
    log_dir = base_dir / 'logs'
    log_dir.mkdir(parents=True,exist_ok=True)
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s in %(module)s:%(message)s',
        handlers=[
            logging.FileHandler(str(log_dir/'app.log'),encoding='utf-8'),
            logging.StreamHandler()
        ]
        )
    # app.logger 自动继承上面的配置
    app.logger.info('应用启动成功')

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
        app.logger.error(f"服务器内部错误: {error}")
        return {"error": "服务器内部错误，请稍后重试"}, 500

    @app.errorhandler(Exception)
    def handle_all_exceptions(error):
        # 捕获所有未处理的异常，确保返回统一格式
        app.logger.error(f"未捕获的异常: {error}")
        return {"error": "服务器内部错误，请稍后重试"}, 500
    
    # ---------- 全局钩子 ----------
    @app.before_request
    def log_request_info():
        app.logger.info(f"Request:{request.method} {request.path}")
        
    @app.after_request
    def log_response_info(response):
        app.logger.info(f"Response:{response.status_code}")
        return response
    
    return app

    