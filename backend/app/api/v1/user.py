from flask import Blueprint,request
from ...models import User,Profile
from werkzeug.security import check_password_hash,generate_password_hash
from ...extensions import db


user_bp = Blueprint('user',__name__)


# 新建用户
@user_bp.route("/create_user",methods=["POST"])
def create_user():
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
        return {"error":"用户名小于3个字符"},400
    if len(password)<6:
        return {"error":"密码长度至少6位"},400
    
    # 职位是否不对
    allow_roles=["waiter","customer"]
    
    if role not in allow_roles:
        return {"error":f"职位必须是{",".join(allow_roles)}其中之一"},422
    
    #唯一性校验
    
    if User.query.filter_by(username=username).first():
        return{"error":"该用户名已被占用"},409
    
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
    
    return {
        "message":"用户创建成功",
        "user":user.to_dict()
        
    },201
# 获取用户
@user_bp.route("/<int:user_id>",methods=["GET"])
def get_user_by_id(user_id):
    
    user = User.query.filter_by(id=user_id).first()
    
    if not user:
        return {"error":"资源不存在"},404
    
    return user.to_dict(),200

# 获取所有用户
@user_bp.route("",methods=["GET"])
def get_users():
    users = User.query.all()
    if users:
        return "",200
    
    
# 删除用户
@user_bp.route("/<int:user_id>",methods=["DELETE"])
def delete_user_by_id(user_id):
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
def update_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    
    if not user:
        return{"error":"资源不存在"},404
    
    data = request.get_json()
   
    if not data:
        return {"error":"请求体必须为json格式"},400
    
    if 'username'in data:
        user.username=data["username"]
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