from flask import Blueprint,request
from ...models import Dish
from ...extensions import db

dish_bp = Blueprint("dish",__name__)

# 获取菜品
@dish_bp.route("/<int:dish_id>",methods=["GET"])
def get_dish(dish_id):
    
    dish = Dish.query.get(dish_id)
    
    if not dish:
        return {"error":"请求资源不存在"},404
    
    return dish.to_dict(),200
    
# 获取全部菜品
@dish_bp.route("",methods=["GET"])
def get_dishes():
    
    # 获取分页参数
    page = request.args.get("page",1,type=int)
    per_page = request.args.get("per_page",10,type=int)
    
    # 获取过滤参数
    keyword = request.args.get("keyword","").strip()
    is_sold_out_str= request.args.get("is_sold_out")
    
    # 构建查询
    query = Dish.query
    if keyword:
        query = query.filter(Dish.dish_name.contains(keyword))
    
    if is_sold_out_str is not None:
        is_sold_out = is_sold_out_str.lower() in ("true","1")
        query = query.filter_by(is_sold_out=is_sold_out)
    # 分页执行
    paginated = query.order_by(Dish.id.desc()).paginate(page=page,per_page=per_page,error_out=False)
    
    # 返回结果
    return {
        "items":[dish.to_dict() for dish in paginated.items],
        "total":paginated.total,
        "page":page,
        "per_page":per_page,
        "pages":paginated.pages,
        "has_next":paginated.has_next,
        "has_prev":paginated.has_prev
    },200
        

# 添加菜品
@dish_bp.route("",methods=["POST"])
def create_dish():
    
    '''
    请求体：
    {
        "dish_name":"清炒白菜",     # 必填
        "price":"10",              # 必填
        "dish_number":"100",       # 必填
        "is_sold_out":"False"      # 可选
    }
    '''
    data = request.get_json()
    
    if not data:
        return {"error":"请求体必须为 JSON 格式"},400
    
    dish_name = data.get("dish_name","").strip()
    price_str = data.get("price",0)
    dish_number_str = data.get("dish_number",0)

    # 必填校验
    if not dish_name or not price_str or not dish_number_str:
        return {"error":"必填项不能为空"},400
    
    try:
        price=float(price_str)
        dish_number= int(dish_number_str)
    except ValueError:
        return {"error":"价格必须是数字，数量必须是整数"},400
    
    dish = Dish(dish_name=dish_name,price=price,dish_number=dish_number)
    
    # 提交数据库
    try:
        db.session.add(dish)
        db.session.commit()
        
    except Exception as e:
        return {"error":f"服务器内部错误{e}"},500
    
    return dish.to_dict(),201

# 更新菜品
@dish_bp.route("/<int:dish_id>",methods=["PATCH"])
def update_dish(dish_id):
    dish = Dish.query.get(dish_id)
    
    if not dish:
        return {"error":"请求资源不存在"},404
        
    data = request.get_json()
    
    if not data:
        return {"error":"请求体必须为json格式"},400
    
    if 'dish_name' in data:
        dish.dish_name = data["dish_name"].strip()
    if 'price' in data:
        try:
            dish.price = float(data["price"])
        except ValueError:
            return {"error":"价格必须是数字"},400
        
        
    if 'dish_number' in data:
        try:
            dish.dish_number = int(data["dish_number"])
        except ValueError:
            return {"error":"数量必须是整数"},400
    
    if 'is_sold_out' in data:
        dish.is_sold_out = bool(data["is_sold_out"])
        
    try:
        db.session.commit()
    
    except Exception as e:
        return {"error":"服务器内部错误"},500
    
    return dish.to_dict(),200
    
   
# 删除菜品
@dish_bp.route("/<int:dish_id>",methods=["DELETE"])
def delete_dish(dish_id):
    dish = Dish.query.get(dish_id)
    
    if not dish:
        return {"error":"请求资源不存在"},404
    
    try:
        db.session.delete(dish)
        db.session.commit()
        
    except Exception as e:
        return {"error":"服务器内部错误"},500

    return "",204