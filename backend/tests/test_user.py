import pytest
from app.models import User
from app import create_app
from app.extensions import db

@pytest.fixture
def client():
    app = create_app(
        {
            "TESTING":True,
            "SQLALCHEMY_DATABASE_URI":"sqlite:///:memory:"
        }
    )
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

@pytest.fixture
def admin_token(client):
    '''注册一个管理员账号并返回token'''
    
    # 注册管理员账号
    client.post("/api/v1/auth/register",
    json={
        "username":"admin",
        "password":"admin123"
    }           
    )
    with client.application.app_context():
        from app.models import User
        user = db.session.query(User).filter_by(username="admin").first()
        user.role ="admin"
        db.session.commit()
    
    # 获取token
    resp = client.post("/api/v1/auth/login",
        json={
            "username":"admin",
            "password":"admin123"
        }               
        )
    
    return resp.json["access_token"]

def register_user(client,username,password):
    return client.post("/api/v1/auth/register",
        json={
            "username":username,
            "password":password
        }
        )

# 测试用例1：获取单个用户
def test_get_user_success(client,admin_token):
    register_user(client,"test_user","test_user123")
    
    resp = client.post("/api/v1/auth/login",
        json={
            "username":"test_user",
            "password":"test_user123"
        }
        )
    user_id = resp.json["user"]["id"]
    
    resp = client.get(f"/api/v1/users/{user_id}",headers={"Authorization":f"Bearer {admin_token}"})
    
    assert resp.status_code==200
    assert resp.json["username"] =="test_user"
    
# 测试用例2：获取多个用户
def test_get_users_success(client,admin_token):
    register_user(client,"test_user1","test_user1123")
    register_user(client,"test_user2","test_user2123")
   
    resp = client.get(f"/api/v1/users",
            query_string={"page":1,"per_page":10},
            headers={"Authorization":f"Bearer {admin_token}"}
            )

    assert resp.status_code==200
    assert resp.json["total"]>=2
    
    
# 测试用例3：增加一个用户
def test_create_users_success(client,admin_token):

    resp = client.post("/api/v1/users",
            json={"username":"test_user","password":"test_user123"},
            headers={"Authorization":f"Bearer {admin_token}"}
            )

    assert resp.status_code==201
    assert resp.json["username"] =="test_user"
    
# 测试用例4：删除一个用户
def test_delete_users_success(client,admin_token):
    temp_resp = register_user(client,"delete_user","delete_user123")
    user_id =temp_resp.json["user"]["id"]
    
    resp = client.delete(f"/api/v1/users/{user_id}",
            headers={"Authorization":f"Bearer {admin_token}"}
            )

    assert resp.status_code==204
    
# 测试用例5：修改一个用户
def test_update_user_success(client,admin_token):
    temp_resp = register_user(client,username="update_user",password="update_user123")
    user_id = temp_resp.json["user"]["id"]
    
    resp = client.patch(f"/api/v1/users/{user_id}",
        json={
            "username":"new_user"
        },
        headers={
            "Authorization":f"Bearer {admin_token}"
        }
        )
    assert resp.status_code==200
    assert resp.json["username"]=="new_user"
    
    