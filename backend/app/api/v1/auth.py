from flask import Blueprint

auth_bp = Blueprint('auth',__name__,url_prefix='/auth')

# 登录功能
@auth_bp.route("/auth/login",methods=["POST"])
def login(username,password):
    pass
# 注册功能
@auth_bp.route("/auth/register",methods=["POST"])
def login(username,password):
    pass
   
# 登出功能
@auth_bp.route("/auth/logout",methods=["POST"])
def login(username,password):
    pass