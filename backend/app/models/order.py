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

    # 订单金额
    total_price =db.Column(db.Numeric(10, 2),nullable=False,default=0.00)
    
    # 订单状态  pending待付款   completed已完成 canceled 已取消
    status = db.Column(db.String(20),nullable=False,default='pending')
    
    # 添加时间
    created_at=db.Column(db.DateTime,default=lambda: datetime.now())
    
    # 结单时间
    finished_at = db.Column(db.DateTime, default=lambda: datetime.now(), onupdate=lambda: datetime.now())

    # 外键 关联user表
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
        
    # 关联菜品表
    dishes = db.relationship('Dish',secondary=order_dish_table,back_populates='orders',lazy=True)
    
    # 让 Python 打印对象时显示可读信息。
    # 调试时用 print(User.query.first())
    def __repr__(self):
        return f'<Order {self.order_number}>'
    
    # 转化成字典
    def to_dict(self):
        return{
            "order_number":self.order_number,
            "total_price":str(self.total_price) if self.total_price else "0.00",
            "status":self.status,
            "created_at":self.created_at.isoformat() if self.created_at else None,
            "finished_at":self.finished_at.isoformat() if self.finished_at else None,
            "user_id":self.user_id,
            "dishes":[dish.to_dict() for dish in self.dishes]
        }