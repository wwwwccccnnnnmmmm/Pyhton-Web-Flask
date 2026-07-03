from flask import Blueprint

user_bp = Blueprint('user',__name__)


# 新建用户
@user_bp.route("/users",methods=["POST"])
def create_user():
    pass

# 获取用户
@user_bp.route("/users/<int:user_id>",methods=["GET"])
def get_user_by_id():
    pass

# 删除用户
@user_bp.route("/users/<int:user_id>",methods=["DELETE"])
def delete_user_by_id():
    pass

# 修改用户
@user_bp.route("/users/<int:user_id>",methods=["PUT"])
def update_user():
    pass