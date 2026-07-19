from flask import Blueprint,request
from ...models import User,Profile
from werkzeug.security import check_password_hash,generate_password_hash
from ...extensions import db
from ...utils import token_required,admin_required

user_bp = Blueprint('user',__name__)


# 新建用户
@user_bp.route("",methods=["POST"])
@token_required
@admin_required
def create_user(current_user_id):
    '''
    后台创建用户
    请求体
    {
        "username":"lisi",          #必填
        "password":"lisi123",       #必填
        "real_name":"李四",         #可选
        "phone":"12332112331",      #可选
        "role":"customer",          #可选
    }
    '''
    data = request.get_json()
    if not data:
        return {"error": "请求体必须为 JSON 格式"}, 400
    
    username = data.get("username","").strip()
    password = data.get("password","").strip()
    real_name = data.get("real_name","").strip() or None
    phone = data.get("phone","").strip() or None
    role = data.get("role","customer").strip() or 'customer'
    
    # 必填校验
    if not username or not password:
        return {"error":"请输入用户名和密码"},400
    # 格式校验
    if len(username)<3:
        return {"error":"用户名小于3个字符"},422
    if len(password)<6:
        return {"error":"密码长度至少6位"},422
    
    #唯一性校验
    existing = User.query.filter_by(username=username).first()
    if existing:
        return{"error":"该用户名已被占用"},409
    
    # 职位是否不对
    allow_roles=["waiter","customer"]
    if role not in allow_roles:
        return {"error":f"职位必须是{'，'.join(allow_roles)}其中之一"},422
    
    # 密码哈希
    hash_password = generate_password_hash(password)
    # 创建用户
    user = User(username=username,password_hash=hash_password,is_active=True)
    
    # 是否有real_name 或者 phone
    if real_name or phone:
        user.profile = Profile(real_name=real_name,phone=phone)
        
    # 保存数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        return {"error":f"服务器内部错误{e}"}
    
    return user.to_dict(),201

# 获取用户
@user_bp.route("/<int:user_id>",methods=["GET"])
@token_required
@admin_required
def get_user(current_user_id,user_id):
    
    user = User.query.filter_by(id=user_id).first()
    
    if not user:
        return {"error":"资源不存在"},404
    
    return user.to_dict(),200

# 获取所有用户
@user_bp.route("",methods=["GET"])
@token_required
@admin_required
def get_users(current_user_id):
    
    # 获取分页参数
    page = request.args.get("page",1,type=int)
    per_page = request.args.get("per_page",10,type=int)
    
    # 获取过滤参数
    keyword=request.args.get("keyword","").strip()
    role=request.args.get("role","").strip()
    is_active_str = request.args.get("is_active")
    
    # 构建查询
    query = User.query
    if keyword:
        query = query.filter(User.username.contains(keyword))
    if role:
        query = query.filter_by(role=role)
    
    if is_active_str is not None:
        is_active = is_active_str.lower() in ('true', '1')
        query = query.filter_by(is_active=is_active)

    # 分页执行
    paginated = query.order_by(User.id.desc()).paginate(page=page,per_page=per_page,error_out=False)
    
    return {
        "items":[user.to_dict() for user in paginated.items],
        "total":paginated.total,
        "page":page,
        "per_page":per_page,
        "pages":paginated.pages,
        "has_next":paginated.has_next,
        "has_prev":paginated.has_prev
        
    }
    
# 删除用户
@user_bp.route("/<int:user_id>",methods=["DELETE"])
@token_required
@admin_required
def delete_user_by_id(current_user_id,user_id):
    user = User.query.filter_by(id=user_id).first()
    
    if not user:
        return {"error":"资源不存在"},404
    
    try:
        db.session.delete(user)
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        
        return {"error":"删除失败，可能被其他数据引用"},500

    return "",204

# 修改用户
@user_bp.route("/<int:user_id>",methods=["PATCH"])
@token_required
@admin_required
def update_user(current_user_id,user_id):
    user = User.query.filter_by(id=user_id).first()
    
    if not user:
        return{"error":"资源不存在"},404
    
    data = request.get_json()
   
    if not data:
        return {"error":"请求体必须为json格式"},400
    
    if 'username'in data:
        new_name = data["username"].strip()
        
        # 唯一性校验
        existing = User.query.filter(User.username==new_name,User.id!=user_id).first()
        if existing:
            return {"error":"用户名已被其他用户占用"},409
        
        user.username=new_name
    if 'password'in data:
        user.password_hash=generate_password_hash(data["password"])
    
    if 'role'in data:
        user.role=data["role"]

    if 'is_active'in data:
        user.is_active=bool(data["is_active"])

    if 'real_name' in data or 'phone' in data:
        if not user.profile:
            
            # 先创建空的profile
            user.profile = Profile()
            
        if 'real_name' in data:
            user.profile.real_name = data["real_name"].strip() or None
        if 'phone' in data:
            user.profile.phone = data["phone"].strip() or None
    try:
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        return {"error":"服务器内部错误"},500
    return user.to_dict(),200