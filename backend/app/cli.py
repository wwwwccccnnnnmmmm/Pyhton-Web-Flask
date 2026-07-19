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
    

# ---------- 注册命令到 Flask 应用 ----------
def init_app(app):
    """将自定义命令添加到 Flask CLI 中。"""
    app.cli.add_command(init_db_command)