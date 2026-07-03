from flask import Blueprint,request
from ...models import User,Profile
from werkzeug.security import check_password_hash,generate_password_hash
from ...extensions import db


auth_bp = Blueprint('auth',__name__)

# 登录功能
@auth_bp.route("/login",methods=["POST"])
def login():
    '''
    用户登录接口
    请求体：{"username":"admin","password":"admin123"}
    响应：:{"access_token": "xxx", "user": {...}}
    '''
    data = request.get_json()
    
    # 查看是否为空
    if not data:
        return {"error":"请求体必须为json格式"},400
    
    username=data.get("username")
    password = data.get("password")
    
    # 校验必填字段
    if not username or not password:
        return {"error":"用户名和密码不能为空"},400

    # 数据库查询
    user = User.query.filter_by(username=username).first()
    
    # 验证用户存在且密码正确
    if not user or not check_password_hash(user.password_hash,password):
        return {"error":"用户名或密码错误"},401

    # 成功的话则创建jwt token 等
    return {
        "access_token":"token",
        "token_type":"Bearer",
        "user":{
            "id":user.id,
            "username":user.username,
            "role":user.role
            
        }
    },200



# 注册功能
@auth_bp.route("/register",methods=["POST"])
def register():
    '''
    用户注册接口
    请求体：
    {"
    username":"zhangsan",
    "password":"zhangsan123",
    "real_name":"张三",     可选
    "phone":"13800011111"}  可选
    响应：:
        成功: 201 {"message": "用户创建成功", "user": {...}}
        失败: 400/409/422 带错误信息
    '''
    data = request.get_json()
    
    # 是否有数据    
    if not data:
        return {"error":"请求体必须要json格式"},400
    
    username = data.get("username","").strip()
    password = data.get("password","").strip()
    role = data.get("role", "customer").strip() or "customer"
    real_name = data.get("real_name","").strip() or None
    phone = data.get("phone","").strip() or None
    
    # 必填校验
    if not username or not password:
        return {"error":"用户名和密码不能为空"},400
    
    # 格式校验
    if len(username)<3:
        return {"error":"用户名长度至少3个字符"}, 422
    
    if len(password)<6:
        return {"error":"密码长度至少6位"}, 422
    
    # 用户名唯一性校验
    existing_user  = User.query.filter_by(username=username).first()
    if existing_user:
        return {"error":"账号已存在"},409
    
    # 哈希密码生成
    hashed_password =  generate_password_hash(password)
    user = User(username=username,password_hash =hashed_password,role=role,is_active = True)
    
    # 如果有个人资料 信息
    if real_name or phone:
        user.profile = Profile(
            real_name=real_name,
            phone=phone
        )
    
    # 保存到数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        print(f"注册失败:{e}")
        return {"error":"服务器内部错误，请稍后重试"},500
    
    return {
        "message":"用户创建成功",
        "user":{
            user.to_dict()
        
    }
        },201
    
# 登出功能
@auth_bp.route("/logout",methods=["POST"])
def logout():
    return {"message":"登出成功，清除本地Token"},200