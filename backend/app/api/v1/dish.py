from flask import Blueprint,request,current_app
from ...models import Dish
from ...extensions import db
from ...utils import admin_required,token_required
from pathlib import Path
from werkzeug.utils import secure_filename
from datetime import datetime

# 允许上传的文件类型
ALLOWED_EXTENSIONS ={"png","jpg","gif","jpeg"}

# 检测
def allowed_file(filename):
    '''检查文件扩展名是否允许'''
    return "." in filename and filename.rsplit(".",1)[1].lower() in ALLOWED_EXTENSIONS

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
@token_required
@admin_required
def create_dish(current_user_id):
    
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
    price_str = data.get("price","").strip()
    dish_number_str = data.get("dish_number","").strip()

    # 必填校验
    if not dish_name or not price_str or not dish_number_str:
        return {"error":"必填项不能为空"},400
    
    # 重复校验
    if Dish.query.filter_by(dish_name=dish_name).first():
        return {"error":"名称已存在"},409
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
@token_required
@admin_required
def update_dish(current_user_id,dish_id):
    dish = Dish.query.get(dish_id)
    
    if not dish:
        return {"error":"资源不存在"},404
        
    data = request.get_json()
    
    if not data:
        return {"error":"请求体必须为json格式"},400
    
    if 'dish_name' in data:
        new_name = data["dish_name"].strip()
        existing = Dish.query.filter(Dish.dish_name==new_name,Dish.id!=dish_id).first()
        if existing:
            return {"error":"菜品名称已被其他菜品占用"},409
        dish.dish_name = new_name
        
    if 'price' in data:
        try:
            dish.price = float(data["price"])
        except ValueError:
            return {"error":"价格必须是数字"},400
        
    if 'category' in data:
       
        dish.category = data["category"]
        
            
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
    
# 上传菜品图
@dish_bp.route("/<int:dish_id>/upload_image",methods=["POST"])
@token_required
@admin_required
def upload_dish_image(current_user_id,dish_id):
    '''
    上传菜品图片
    请求体：form-data,字段名file
    返回{"img_url":"/static/uploads/XXXXX.jpg"}
    '''
    
    MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB
    
    # backend 文件路径
    base_dir = Path(current_app.root_path).parent
    #菜品上传文件路径
    dish_img_dir= base_dir / 'static' / 'uploads' / 'dishes'
    dish_img_dir.mkdir(parents=True,exist_ok=True)
    
    dish = Dish.query.get(dish_id)
    if not dish:
        return {"error":"资源不存在"},404
    
    # 1.获取文件
    if 'file' not in request.files:
        return {"error":"没有文件上传"},400
    
    file = request.files["file"]
    
    if file.filename =="":
        return {"error":"文件名不能为空"},400

    # 校验文件类型（jpg,png)
    if not allowed_file(file.filename):
        return {"error":"只支持jpg/gif/jpeg/png格式"},400
    
    if request.content_length and request.content_length > MAX_FILE_SIZE:
        return {"error": f"文件大小超过限制，最大支持 {MAX_FILE_SIZE // (1024*1024)}MB"}, 413

    # 获取文件扩展名
    original_ext = file.filename.rsplit(".",1)[1].lower()
    
    name_part = secure_filename(file.filename).rsplit('.',1)[0]
    # 生成安全名称
    safe_filename =f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{name_part}.{original_ext}"
 
    # 保存到static/uploads
    file_path = dish_img_dir / safe_filename
    
    try:
        file.save(str(file_path))
    except Exception as e:
        return {"error":f"文件保存失败:{str(e)}"},500
    
    # 返回图片URL
    img_url = f"/static/uploads/dishes/{safe_filename}"
    dish.dish_img = img_url
    db.session.commit()
    
    return {
        "message":"上传成功",
        "img_url":img_url,
        "filename":safe_filename
    },201
    
# 删除菜品
@dish_bp.route("/<int:dish_id>",methods=["DELETE"])
@token_required
@admin_required
def delete_dish(current_user_id,dish_id):
    dish = Dish.query.get(dish_id)
    
    if not dish:
        return {"error":"请求资源不存在"},404
    
    try:
        db.session.delete(dish)
        db.session.commit()
        
    except Exception as e:
        return {"error":"服务器内部错误"},500

    return "",204