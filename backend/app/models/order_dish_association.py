from ..extensions import db

order_dish_table = db.Table(
    'order_dish',
    db.Column('order_id',db.Integer,db.ForeignKey("orders.id"),primary_key=True),
    db.Column('dish_id',db.Integer,db.ForeignKey("dishes.id"),primary_key=True)
    )