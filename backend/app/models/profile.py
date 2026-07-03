from ..extensions import db
from datetime import datetime

class Profile(db.Model):
    # 表名
    __tablename__ ='profiles'
    
    # 字段
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    real_name=db.Column(db.String(50),nullable=True)
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(20),unique=True)    
    avatar_url = db.Column(db.String(255),nullable=True)
    hire_date = db.Column(db.DateTime,nullable=True)
    
    employee_id = db.Column(db.String(20),nullable=True,unique=True)
    position=db.Column(db.String(20), nullable=True)
    # onupdate=datetime.now更新记录时，自动将时间改为当前时间。
    updated_at=db.Column(db.DateTime,default=datetime.now,onupdate=datetime.now)
    
    # 外键 关联用户表
    user_id = db.Column(db.Integer,db.ForeignKey("users.id"), unique=True,nullable=False)
    
    user = db.relationship("User",back_populates="profile", uselist=False)
    
    
    # 让 Python 打印对象时显示可读信息。
    def __repr__(self):
        return f'<Profile {self.real_name}>'
    
    # 转化成字典
    def to_dict(self):
        return{
            "id":self.id,
            "real_name":self.real_name,
            "email":self.email,
            "employee_id":self.employee_id,
            "phone":self.phone,
            "updated_at":self.updated_at.isoformat() if self.updated_at else None
        }
        
   
    