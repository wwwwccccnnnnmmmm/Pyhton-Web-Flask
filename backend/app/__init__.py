from flask import Flask,request
from .config import Config
from .api.v1 import user_bp,auth_bp,dish_bp,order_bp
from .extensions import db,migrate
from flask_cors import CORS
import logging
from pathlib import Path
import click
from .models import User,Dish
from werkzeug.security import generate_password_hash

def create_app(config_override=None):
    
    # 创建 Flask 核心实例
    app = Flask(__name__)
    CORS(app)
    # 从 Config 这个类中加载所有的配置变量
    app.config.from_object(Config)
    
    # 如果有覆盖配置，更新到 app.config
    if config_override:
        app.config.update(config_override)
    
    # 将之前定义好的 db 扩展实例，绑定到当前创建的 app 实例上
    db.init_app(app)
    
    #绑定数据库和应用
    migrate.init_app(app,db)
    
    # 蓝图注册
    app.register_blueprint(user_bp, url_prefix='/api/v1/users')
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(dish_bp, url_prefix='/api/v1/dishes')
    app.register_blueprint(order_bp,url_prefix='/api/v1/orders')
    
    
    
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
        app.logger.exception("未捕获的异常") 
        return {"error": "服务器内部错误，请稍后重试"}, 500
    
    # ---------- 全局钩子 ----------
    @app.before_request
    def log_request_info():
        app.logger.info(f"Request:{request.method} {request.path}")
        
    @app.after_request
    def log_response_info(response):
        app.logger.info(f"Response:{response.status_code}")
        return response
    
    @app.cli.command('seed')
    def seed():
        
        # 检测是否已经有管理员
        if User.query.filter_by(username="admin").first():
            click.echo("管理员已存在")
            return 
        try:
            # 1. 创建管理员
            admin = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                role='admin',
                is_active=True
            )
            
            db.session.add(admin)
            db.session.flush()
            # 2. 创建普通用户
            zhangsan = User(
                username='zhangsan',
                password_hash=generate_password_hash('zhangsan123'),
                role='customer',
                is_active=True
            )
            
            db.session.add(zhangsan)
            db.session.flush()
            
            # 4. 为 admin 创建几道菜
            dish1 = Dish(dish_name='红烧肉', price=58.0,category="荤菜",dish_number=20)
            dish2 = Dish(dish_name='清蒸鲈鱼', price=68.0, category="荤菜",dish_number=15)
            dish3 = Dish(dish_name='麻婆豆腐', price=28.0, category="素菜",dish_number=30)
            dish4 =Dish(dish_name='酸辣土豆丝', price=18.0,category="素菜", dish_number=50)
            
            db.session.add_all([dish1, dish2, dish3, dish4])

            # 提交所有数据
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            click.echo(f"插入失败：{e}")
            
    return app

    