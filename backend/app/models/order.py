from ..extensions import db
from datetime import datetime
from .order_dish_association import order_dish_table

class Order(db.Model):
    # 表名
    __tablename__ ='orders'
    
    # 字段
    
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    
    # 订单编号
    order_number=db.Column(db.String(20),unique=True,nullable=False)

    # 是否结单
    is_finished = db.Column(db.Boolean,nullable=False,default=False)
    
    # 添加时间
    created_at=db.Column(db.DateTime,default=datetime.now)
    
    # 结单时间
    finished_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # 外键 关联user表
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
        
    # 关联菜品表
    dishes = db.relationship('Dish',secondary=order_dish_table,back_populates='orders',lazy=True)
    
    # 让 Python 打印对象时显示可读信息。
    # 调试时用 print(User.query.first())
    def __repr__(self):
        return f'<Dish {self.orders_number}>'
    
    # 转化成字典
    def to_dict(self):
        return{
            "orders_number":self.orders_number,
            "is_finished":self.is_finished,
            "created_at":self.created_at.isoformat() if self.created_at else None,
            "finished_at":self.finished_at.isoformat() if self.finished_at else None,
            "user_id":self.user_id
        }