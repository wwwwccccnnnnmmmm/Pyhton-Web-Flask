from ..extensions import db
from datetime import datetime
from .order_dish_association import order_dish_table

class Dish(db.Model):
    # 表名
    __tablename__ ='dishes'
    
    # 字段
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    
    # 名称
    dish_name=db.Column(db.String(50),unique=True,nullable=False)
    # 价格
    price=db.Column(db.Numeric(10, 2), nullable=False)

    # 库存
    dish_number = db.Column(db.Integer,nullable=False, default=0)
    
    # 是否卖完
    is_sold_out=db.Column(db.Boolean, default=False)
    
    # 添加时间
    created_at=db.Column(db.DateTime,default=lambda: datetime.now())
    
    # 更新时间
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(), onupdate=lambda: datetime.now())

    # 外键 关联user表
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False, default=1)
    
    creator = db.relationship("User",back_populates='dishes',lazy=True)
    
    # 关联order表
    orders = db.relationship('Order',secondary=order_dish_table,back_populates='dishes',lazy=True)
    # 让 Python 打印对象时显示可读信息。
    # 调试时用 print(User.query.first()) 。
    def __repr__(self):
        return f'<Dish {self.dish_name}>'
    
    # 转化成字典
    def to_dict(self):
        return{
            "id":self.id,
            "dish_name":self.dish_name,
            "price":str(self.price),
            "dish_number":self.dish_number,
            "is_sold_out":self.is_sold_out,
            "created_at":self.created_at.isoformat() if self.created_at else None,
            "updated_at":self.updated_at.isoformat() if self.updated_at else None
        }