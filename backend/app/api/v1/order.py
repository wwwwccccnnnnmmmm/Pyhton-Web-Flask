from decimal import Decimal
from flask import Blueprint,request
from ...extensions import db
from ...models import Order,Dish
from ...utils import generate_order_number,token_required,admin_required

order_bp = Blueprint("order",__name__)

# 获取订单
@order_bp.route("/<int:order_id>",methods=["GET"])
@token_required
@admin_required
def get_order(current_user_id,order_id):
    
    order = Order.query.get(order_id)
    if not order:
        return {"error":"资源不存在"},404
    
    return order.to_dict(),200

# 获取某一个用户的订单
@order_bp.route("/my",methods=["GET"])
@token_required
def get_my_orders(current_user_id):
    page = request.args.get("page",1,type=int)
    per_page = request.args.get("per_page",10,type=int)
    
    paginated = Order.query.filter_by(user_id=current_user_id)\
    .order_by(Order.created_at.desc())\
    .paginate(page=page,per_page=per_page,error_out=False)
    
    return {
        "user_id":current_user_id,
        "orders":[order.to_dict() for order in paginated.items],
        "total":paginated.total,
        "page":page,
        "per_page":per_page,
        "pages":paginated.pages
    },200
    
    
# 获取所有订单
@order_bp.route("",methods=["GET"])
@token_required
@admin_required
def get_orders(current_user_id):
    
    # 获取分页参数
    page = request.args.get("page",1,type=int)
    per_page = request.args.get("per_page",10,type=int)
    
    # 获取过滤参数
    keyword=request.args.get("keyword","").strip()
    status = request.args.get("status","").strip()
    
    # 构建查询
    query = Order.query
    if keyword:
        query = query.filter(Order.order_number.contains(keyword))
    if status:
        query = query.filter_by(status=status)
    
    #分页执行
    paginated = query.order_by(Order.id.desc()).paginate(page=page,per_page=per_page,error_out=False)
    
    # 返回结果
    return {
        "items":[order.to_dict() for order in paginated.items],
        "total":paginated.total,
        "page":page,
        "per_page":per_page,
        "pages":paginated.pages,
        "has_next":paginated.has_next,
        "has_prev":paginated.has_prev
    }

# 创建订单
@order_bp.route("",methods=["POST"])
@token_required
def create_order(current_user_id):
    
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
    
    order_number = generate_order_number()
    
    while Order.query.filter_by(order_number=order_number).first():
        order_number = generate_order_number()

    dishes_data = data.get("dishes",[])
    
    # 必填校验
    if not order_number:
        return {"error":"订单编号不能为空"},400

    if not dishes_data or not isinstance(dishes_data,list):
        return {"error":"请提供有效的菜品列表"},400

    order = Order(order_number=order_number,user_id=current_user_id)
    
    
    # 遍历菜品避免不存在某些菜
    for item in dishes_data:
        dish_name = item.get("dish_name","").strip()
        quantity = item.get("quantity", 1)
        
        if not dish_name:
            return {"error":"每个菜品必须包含dish_name"},400
        
        if not isinstance(quantity,int) or quantity<=0:
            return {"error":f"菜品{dish_name}的数量必须是正整数"},400
        
        # 数据库查找
        dish = Dish.query.filter_by(dish_name=dish_name).first()
        
        if not dish:
            return {"error":"资源不存在"},404
    
    dish_object = []
    total_price = Decimal("0.00")
    
    # 遍历菜品进行价格相加
    for item in dishes_data:
        dish_name = item.get("dish_name","").strip()
        quantity = item.get("quantity",1)

        # 数据库查找
        dish = Dish.query.filter_by(dish_name=dish_name).first()
        
        total_price +=dish.price * quantity
        
        dish_object.append(dish)
        
    order.total_price = total_price
    order.dishes.extend(dish_object)
    
    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        return {"error":"服务器内部错误"},500
    
    return order.to_dict(),201

# 修改订单
@order_bp.route("/<int:order_id>",methods=["PATCH"])
@token_required
@admin_required
def update_order(current_user_id,order_id):
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
    
# 用户取消订单
@order_bp.route("/<int:order_id>/cancel",methods=["PATCH"])
@token_required
def canceled_order(current_user_id,order_id):
    order = Order.query.get(order_id)
    if not order:
        return {"error":"资源不存在"},404
    if order.user_id !=current_user_id:
        return {"error":"无权操作此订单"},403
    if order.status !='pending':
        return {"error":"只有待付款订单可以取消"},400
    order.status = 'canceled'
    db.session.commit()
    return {"message":"该订单已取消"},200

# 删除订单
@order_bp.route("/<int:order_id>",methods=["DELETE"])
@token_required
def delete_order(current_user_id,order_id):
    order = Order.query.get(order_id)
    
    if not order:
        return{"error":"资源不存在"},404
    try:
        db.session.delete(order)
        db.session.commit()
    except Exception as e:
        return {"error":"服务器内部错误"},500

    return "",204