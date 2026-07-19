
import pytest
from app import create_app
from app.extensions import db
from app.models import User,Dish
import io

# 创建测试客户端口
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

# admin_token
@pytest.fixture
def admin_token(client):
    # 1.创建一个admin
    client.post("/api/v1/auth/register",
        json={
            "username":"admin",
            "password":"admin123"
        }
        )
    with client.application.app_context():
        # 2.role设置为admin
        user = db.session.query(User).filter_by(username="admin").first()
        if user.role !="admin":
            user.role = "admin"
            db.session.commit()
        
    # 3.登录 获取他的token
    resp = client.post("/api/v1/auth/login",
        json={
            "username":"admin",
            "password":"admin123"
            
        }
        
        )
    return resp.json["access_token"]

# 测试用例1 增加菜品
def test_create_dish_success(client,admin_token):
    resp = client.post("/api/v1/dishes",
        json={
            "dish_name":"辣白菜",
            "price":"100.0",
            "dish_number":"30"
        },
        headers={
            "Authorization":f"Bearer {admin_token}"
        }        
        )
    assert resp.status_code ==201
    assert resp.json["dish_name"] == "辣白菜"
    
# 测试用例2 删除菜品
def test_delete_dish_success(client,admin_token):
    
    existed_resp = client.post("/api/v1/dishes",
        json={
            "dish_name":"辣白菜",
            "price":"100.0",
            "dish_number":"30"
        },
        headers={
            "Authorization":f"Bearer {admin_token}"
        }        
        )
    dish_id =existed_resp.json["id"]
    resp = client.delete(f"/api/v1/dishes/{dish_id}",
        headers={
            "Authorization":f"Bearer {admin_token}"
        }        
        )
    
    assert resp.status_code ==204
    
# 测试用例3 修改菜品
def test_update_dish_success(client,admin_token):
    existed_resp = client.post("/api/v1/dishes",
        json={
            "dish_name":"辣白菜",
            "price":"100.0",
            "dish_number":"30"
        },
        headers={
            "Authorization":f"Bearer {admin_token}"
        }        
        )
    dish_id = existed_resp.json["id"]
    
    resp = client.patch(f"/api/v1/dishes/{dish_id}",
        json={
            "dish_name":"修改过的辣白菜",
        },
        headers={
            "Authorization":f"Bearer {admin_token}"
        }
        )
    assert resp.json["dish_name"] == "修改过的辣白菜"
    assert resp.status_code ==200
    
# 测试用例4 查找一个菜品
def test_get_dish_success(client,admin_token):
    temp_resp = client.post("/api/v1/dishes",
        json={
            "dish_name":"辣白菜",
            "price":"100.0",
            "dish_number":"30"
        },
        headers={
            "Authorization":f"Bearer {admin_token}"
        }        
        )
    dish_id = temp_resp.json["id"]
    resp = client.get(f"/api/v1/dishes/{dish_id}",
        
        headers={
            "Authorization":f"Bearer {admin_token}"
        }        
        )
    assert resp.status_code ==200
    assert resp.json["dish_name"]=="辣白菜"
    
# 测试用例5 查找多个菜品
def test_get_dishes_success(client,admin_token):
    client.post("/api/v1/dishes",
        json={
            "dish_name":"辣白菜",
            "price":"100.0",
            "dish_number":"30"
        },
        headers={
            "Authorization":f"Bearer {admin_token}"
        }        
        )
    
    client.post("/api/v1/dishes",
        json={
            "dish_name":"炒年糕",
            "price":"100.0",
            "dish_number":"30"
        },
        headers={
            "Authorization":f"Bearer {admin_token}"
        }        
        )
    resp =client.get(f"/api/v1/dishes",
        query_string={
            "page":1,
            "per_page":10
        },
        headers={
            "Authorization":f"Bearer {admin_token}"
        }     
        )
    assert resp.status_code ==200
    assert resp.json["total"]>=1
    
# 测试用例6 上传菜品图
def test_upload_dish_img_success(client,admin_token):
    create_resp = client.post(f"/api/v1/dishes",
        json={
            "dish_name":"带图作品",
            "price":"100.0",
            "dish_number":"30"
        },
        headers={
            "Authorization":f"Bearer {admin_token}"
        }        
        )
    dish_id = create_resp.json["id"]
    
    # 构建一个假的图片文件
    fake_img = io.BytesIO()
    fake_img.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82')
    fake_img.seek(0)
    
    # 上传图片
    resp = client.post(f"/api/v1/dishes/{dish_id}/upload_image",
        data={
            "file":(fake_img,"test.png"),
            
        },
        headers={
            "Authorization":f"Bearer {admin_token}"
        }        
        )
    assert resp.status_code ==201
    assert 'img_url' in resp.json
    dish = db.session.get(Dish,dish_id)
    assert dish.dish_img ==resp.json["img_url"]
    