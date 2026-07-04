from flask import Blueprint,request
from ...extensions import db
from ...models import Order,Dish

order_bp = Blueprint("order",__name__)

# 获取订单
@order_bp.route("/<int:order_id>",methods=["GET"])
def get_order(order_id):
    
    order = Order.query.get(order_id)
    if not order:
        return {"error":"资源不存在"},404
    
    return order.to_dict(),200
    
# 获取所有订单
@order_bp.route("",methods=["GET"])
def get_orders():
    pass
  

# 创建订单
@order_bp.route("",methods=["POST"])
def create_order():
    
    '''
    请求体：
    {
        "order_number":"",
        "dishes":[
            {
            "dish_name":"水煮青菜",
            "price":10
        },
        {
            "dish_name":"红烧肉",
            "price":30
        },
        ]
    }
    '''
    
    data = request.get_json()
    
    if not data:
        return {"error":"请求体必须为json格式"},400
    
    order_number = data.get("order_number","").strip()
    dishes_data = data.get("dishes",[])
    
    # 必填校验
    if not order_number:
        return {"error":"订单编号不能为空"},400
    
    if not dishes_data or not isinstance(dishes_data,list):
        return {"error":"请提供有效的菜品列表"},400

    order = Order(order_number=order_number)
    
    dish_object = []
    # 遍历菜品
    for item in dishes_data:
        dish_name = item.get("dish_name","").strip()
        price = item.get("price",0)
        
        if not dish_name or not price:
            return {"error":"每个菜品必须包含dish_name和price"},400
        
        # 数据库查找
        dish = Dish.query.filter_by(dish_name=dish_name).first()
        
        if not dish:
            return {"error":"资源不存在"},404
        
        dish_object.append(dish)
        
    order.dishes.extend(dish_object)
    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        return {"error":"服务器内部错误"},500
    
    return order.to_dict(),201

# 修改订单
@order_bp.route("/<int:order_id>",methods=["PATCH"])
def update_order(order_id):
    order = Order.query.get(order_id)
    
    if not order:
        return {"error":"资源不存在"},404
    
    data = request.get_json()
    
    if not data:
        return{"error":"请求体必须为json格式"},400
    
    if 'dishes' in data:
        dishes_data=data["dishes"]
        if not isinstance(dishes_data,list):
            return {"error":"dishes必须是列表"},400
        
        # 清空原先所有菜品
        order.dishes.clear()
        
        dish_object = []
        
        for item in dishes_data:
            dish_name = item.get("dish_name","").strip()
            price = item.get("price",0)
            
            if not dish_name or not price:
                return {"error":"每个菜品必须包含dish_name和price"},400
            
            # 数据库查找
            dish = Dish.query.filter_by(dish_name=dish_name).first()
            if not dish:
                return {"error":"资源不存在"},404
            
            dish_object.append(dish)
            
        order.dishes.extend(dish_object)
            
    try:
        db.session.commit()
    except Exception as e:
        return {"error":"服务器内部错误"},500
    
    return order.to_dict(),200
    
    

# 删除订单
@order_bp.route("/<int:order_id>",methods=["DELETE"])
def delete_order(order_id):
    order = Order.query.get(order_id)
    
    if not order:
        return{"error":"资源不存在"},404
    try:
        db.session.delete(order)
        db.session.commit()
    except Exception as e:
        return {"error":"服务器内部错误"},500

    return "",204