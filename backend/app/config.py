import os

class Config:
    
    # 密钥
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    
    # 数据库配置(告诉SQLALCHEMY要连接哪个数据库)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///canteen.db')
    
    # 关闭对每个数据对象的修改追踪 如果不关，Flask 会在内存里记录对每个数据对象的修改历史，会占用额外内存。
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT令牌过期时间
    JWT_EXPIRATION_HOURS = 24
    
    
    