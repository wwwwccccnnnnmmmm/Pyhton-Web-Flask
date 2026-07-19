from datetime import datetime,timedelta
from flask import current_app,request
import jwt
from functools import wraps
from ..models import User

def generate_token(user_id:int) -> str:
    '''
    生成JWT Token
    调用时机：用户登录成功后
    '''
    
    payload ={
        "user_id":user_id,
        "exp":datetime.now() + timedelta(hours=current_app.config.get("JWT_EXPIRATION_HOURS",24))
    }
    return jwt.encode(payload,current_app.config["SECRET_KEY"], algorithm="HS256")

def token_required(f):
    '''
    装饰器:验证Token 并注入当前用户ID
    用法：在需要登陆的接口上添加@token_required
    
    '''
    @wraps(f)
    def decorated(*args,**kwargs):
        print("token_required called")
        # 获取请求头中的Authorization
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return {"error":"Token缺失或格式错误"},401
        
        token = auth_header.split(" ")[1]
        
        # 解码并验证token
        try:
            payload = jwt.decode(token,current_app.config["SECRET_KEY"], algorithms=['HS256'])
            current_user_id = payload.get('user_id')
        except jwt.ExpiredSignatureError:
            return {"error":"Token已过期"},401
        except jwt.InvalidTokenError:
            return {"error":"Token无效"},401
        
        #把当前用户id 作为参数传递给视图函数
        return f(current_user_id,*args,**kwargs)
    return decorated

def admin_required(f):
    '''
    管理员权限装饰器
    用法：在需要管理员权限的接口上添加@admin_required
    注意：必须配合@token_required使用
    '''
    @wraps(f)
    def decorated(current_user_id,*args,**kwargs):
        
        # 查询用户
        user = User.query.get(current_user_id)
        if not user:
            return {"error":"用户不存在"},404
        
        #检查是否为管理员
        if user.role !='admin':
            return {"error":"需要管理员权限"},403
        
        # 权限通过,执行原视图函数
        return f(current_user_id,*args,**kwargs)
    
    return decorated

    
        
