from werkzeug.datastructures import headers

import pytest
from app import create_app
from app.extensions import db

# 创建Flask测试实例

@pytest.fixture
def client():
    app =create_app(
        {"TESTING":True,
        "SQLALCHEMY_DATABASE_URI":"sqlite:///:memory:"
        }
    )
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

# 测试用例1：注册成功
def test_register_success(client):
    resp = client.post("/api/v1/auth/register",
                       json={
                           "username":"test_user",
                           "password":"test_user123"
                       }
                       )
    
    assert resp.status_code ==201
    assert resp.json["user"]["username"] =="test_user"
    
# 测试用例2：注册重复用户
def test_register_duplicate(client):
    client.post("/api/v1/auth/register",
        json={
            "username":"duplicate",
            "password":"duplicate123"
        }
        )
    
    resp =  client.post("/api/v1/auth/register",
        json={
            "username":"duplicate",
            "password":"duplicate123"
        }
        )
    
    assert resp.status_code ==409
    assert "已存在" in resp.json["error"]

# 测试用例3：登录成功
def test_login_success(client):
    
    client.post("/api/v1/auth/register",
        json={
            "username":"test_user",
            "password":"test_user123"
        }
        )
    
    resp = client.post("/api/v1/auth/login",
        json={
            "username":"test_user",
            "password":"test_user123"
        }
        )
    
    assert resp.status_code ==200
    assert "access_token" in resp.json 

# 测试用例4：获取个人资料
def test_me_success(client):
    
    client.post("/api/v1/auth/register",
        json={
            "username":"test_user",
            "password":"test_user123"
        }               
        )
    
    resp = client.post("/api/v1/auth/login",
        json={
            "username":"test_user",
            "password":"test_user123"
        }        
        )
    token = resp.json["access_token"]
    
    me_resp = client.get("/api/v1/auth/me",
        headers={
            "Authorization":f"Bearer {token}"
        }
        )
    assert me_resp.status_code==200
    assert me_resp.json["username"] =="test_user"

# 测试用例6：获取并修改自己的个人资料
def test_update_me_profile(client):
    
    # 创建一个用户
    client.post("/api/v1/auth/register",
        json={
            "username":"test_user",
            "password":"test_user123"
        }               
        )
    # 然后登陆
    get_id_resp = client.post("/api/v1/auth/login",
        json={
            "username":"test_user",
            "password":"test_user123"
        }               
        )
    token = get_id_resp.json["access_token"]
    
    # 然后修改内容
    resp = client.patch("/api/v1/auth/me",
        json={
            "real_name":"test_user_名字",
            "email":"test_emaiL@qq.com",
            "phone":"19282792929"
        },
        headers={
            "Authorization":f"Bearer {token}"
        }
            )
    assert resp.status_code==200
    assert resp.json["real_name"] =="test_user_名字"