import click
from werkzeug.security import generate_password_hash
from datetime import datetime

from app.extensions import db
from app.models import User,Dish,Profile

@click.command('init-db')
def init_db_command():
    """清空数据库，重建表结构并插入测试数据。"""
    click.echo(" 正在删除旧表...")
    db.drop_all()
    click.echo(" 正在创建新表...")
    db.create_all()

    # ---- 插入测试数据 ----
    # 1. 创建管理员
    admin = User(
        username='admin',
        password_hash=generate_password_hash('admin123'),
        role='admin',
        is_active=True
    )

    # 3. 为 admin 创建 Profile
    admin.profile = Profile(
        real_name='管理员',
        phone='13800138000',
        employee_id='EMP001',
        position='店长',
        hire_date=datetime.now()
    )
    db.session.add(admin)
    
    # 2. 创建普通用户
    zhangsan = User(
        username='zhangsan',
        password_hash=generate_password_hash('zhangsan123'),
        role='customer',
        is_active=True
    )
    
    zhangsan.profile = Profile(
        real_name='张三',
        phone='13800138001',
        employee_id='EMP002',
        position='服务员',
        hire_date=datetime.now()
    )
    
    db.session.add(zhangsan)

   

    # 4. 为 admin 创建几道菜
    dish1 = Dish(dish_name='红烧肉', price=58.0,category="荤菜",dish_number=20)
    dish2 = Dish(dish_name='清蒸鲈鱼', price=68.0, category="荤菜",dish_number=15)
    dish3 = Dish(dish_name='麻婆豆腐', price=28.0, category="素菜",dish_number=30)
    dish4 =Dish(dish_name='酸辣土豆丝', price=18.0,category="素菜", dish_number=50)
    zhangsan.dishes.append(dish1)
    zhangsan.dishes.append(dish2)
    zhangsan.dishes.append(dish3)
    zhangsan.dishes.append(dish4)

    db.session.add_all([dish1, dish2, dish3, dish4])

    # 提交所有数据
    db.session.commit()

# ---------- 注册命令到 Flask 应用 ----------
def init_app(app):
    """将自定义命令添加到 Flask CLI 中。"""
    app.cli.add_command(init_db_command)