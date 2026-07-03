from ..extensions import db
from datetime import datetime

class User(db.Model):
    # 表名
    __tablename__ ='users'
    
    # 字段
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    username=db.Column(db.String(50),unique=True,nullable=False)
    password_hash=db.Column(db.String(128), nullable=False)
    role=db.Column(db.String(20),nullable=False,default='customer')
    is_active=db.Column(db.Boolean, default=True)
   
    created_at=db.Column(db.DateTime,default=datetime.now)
    
    # onupdate=datetime.now更新记录时，自动将时间改为当前时间。
    updated_at=db.Column(db.DateTime,default=datetime.now,onupdate=datetime.now)
    
    # 关联菜品表
    dishes = db.relationship("Dish",back_populates='creator',lazy=True)
    
    # 关联 个人信息表
    profile = db.relationship("Profile",back_populates="user",uselist=False)
    
    # 让 Python 打印对象时显示可读信息。
    # 调试时用 print(User.query.first()) 能看到 <User 张三>。
    def __repr__(self):
        return f'<User {self.username}>'
    
    # 转化成字典
    def to_dict(self):
        return{
            "id":self.id,
            "username":self.username,
            "role":self.role,
            "is_active":self.is_active,
            "created_at":self.created_at.isoformat() if self.created_at else None,
            "updated_at":self.updated_at.isoformat()if self.updated_at else None,
            "profile": {
            "real_name": self.profile.real_name if self.profile else None,
            "phone": self.profile.phone if self.profile else None,
            "email": self.profile.email if self.profile else None,
            "avatar_url": self.profile.avatar_url if self.profile else None
        } if self.profile else None
        }