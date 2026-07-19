
from app import create_app
from app.models import User
from app.extensions import db
import pytest

@pytest.fixture
def client():
    app =create_app(
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
    client.post("/api/v1/auth/register",
        json={
            "username":"admin",
            "password":"admin123"
        }        
        )
    
    with client.application.app_context():
        
        user = db.session.query(User).filter_by(username="admin").first()
        if user.role !="admin":
            user.role ="admin"
        db.session.commit()
        
    resp = client.post("/api/v1/auth/login",
        json={
            "username":"admin",
            "password":"admin123"
        }        
        )
    return resp.json["access_token"]

# 测试用例1：增加订单
def test_create_order_success(client,admin_token):
    
     # 先创建菜品（确保数据库中有这些菜）
    client.post("/api/v1/dishes", json={
        "dish_name": "水煮青菜",
        "price": "10",
        "dish_number": "100"
    }, headers={"Authorization": f"Bearer {admin_token}"})
    
    client.post("/api/v1/dishes", json={
        "dish_name": "红烧肉",
        "price": "10",
        "dish_number": "100"
    }, headers={"Authorization": f"Bearer {admin_token}"})


    resp = client.post("/api/v1/orders",
        json={
            "dishes":[
            {
            "dish_name":"水煮青菜",
        },
        {
            "dish_name":"红烧肉",
        },
        ]
        },headers={
            "Authorization":f"Bearer {admin_token}"
        }       
        )
    assert resp.status_code ==201
    
# 测试用例2：删除订单
def test_delete_order_success(client,admin_token):
     # 先创建菜品（确保数据库中有这些菜）
    client.post("/api/v1/dishes", json={
        "dish_name": "水煮青菜",
        "price": "10",
        "dish_number": "100"
    }, headers={"Authorization": f"Bearer {admin_token}"})
    
    client.post("/api/v1/dishes", json={
        "dish_name": "红烧肉",
        "price": "10",
        "dish_number": "100"
    }, headers={"Authorization": f"Bearer {admin_token}"})


    create_resp = client.post("/api/v1/orders",
        json={
            "dishes":[
            {
            "dish_name":"水煮青菜",
            "price":"10"
        },
        {
            "dish_name":"红烧肉",
            "price":"30"
        },
        ]
        },
        headers={
            "Authorization":f"Bearer {admin_token}"
        }       
        )
    order_id = create_resp.json["id"]
    resp = client.delete(f"/api/v1/orders/{order_id}",
        headers={
            "Authorization":f"Bearer {admin_token}"
        } )
    assert resp.status_code ==204
    
# 测试用例3：修改订单
def test_update_order_success(client,admin_token):
    
     # 先创建菜品（确保数据库中有这些菜）
    client.post("/api/v1/dishes", json={
        "dish_name": "水煮青菜",
        "price": "10",
        "dish_number": "100"
    }, headers={"Authorization": f"Bearer {admin_token}"})
    
    client.post("/api/v1/dishes", json={
        "dish_name": "红烧肉",
        "price": "10",
        "dish_number": "100"
    }, headers={"Authorization": f"Bearer {admin_token}"})

    create_resp = client.post("/api/v1/orders",
            json={
                "dishes":[
                {
                "dish_name":"水煮青菜",
                "price":"10"
            },
            {
                "dish_name":"红烧肉",
                "price":"30"
            },
            ]
            },headers={
            "Authorization":f"Bearer {admin_token}"
        }       
            )
    dish_id = create_resp.json["id"]
    
    resp = client.patch(f"/api/v1/orders/{dish_id}",
            json={
                "dishes":[
                {
                "dish_name":"水煮青菜",
                "price":"100"
            },
            {
                "dish_name":"红烧肉",
                "price":"300"
            },
            ]
            },
            headers={
                "Authorization":f"Bearer {admin_token}"
            }       
            )
    assert resp.status_code ==200
    
# 测试用例4：获取具体一个订单
def test_get_order_success(client,admin_token):
     # 先创建菜品（确保数据库中有这些菜）
    client.post("/api/v1/dishes", json={
        "dish_name": "水煮青菜",
        "price": "10",
        "dish_number": "100"
    }, headers={"Authorization": f"Bearer {admin_token}"})
    
    client.post("/api/v1/dishes", json={
        "dish_name": "红烧肉",
        "price": "10",
        "dish_number": "100"
    }, headers={"Authorization": f"Bearer {admin_token}"})

    create_resp = client.post("/api/v1/orders",
            json={
                "dishes":[
                {
                "dish_name":"水煮青菜",
                "price":"10"
            },
            {
                "dish_name":"红烧肉",
                "price":"30"
            },
            ]
            },headers={
            "Authorization":f"Bearer {admin_token}"
        }       
            )
    dish_id = create_resp.json["id"]
    resp = client.get(f"/api/v1/orders/{dish_id}", headers={"Authorization": f"Bearer {admin_token}"})
    
    assert resp.status_code ==200
    assert "dishes" in resp.json
    
# 测试用例5：获取所有订单
def test_get_orders_success(client,admin_token):
     # 先创建菜品（确保数据库中有这些菜）
    client.post("/api/v1/dishes", json={
        "dish_name": "水煮青菜",
        "price": "10",
        "dish_number": "100"
    }, headers={"Authorization": f"Bearer {admin_token}"})
    
    client.post("/api/v1/dishes", json={
        "dish_name": "红烧肉",
        "price": "10",
        "dish_number": "100"
    }, headers={"Authorization": f"Bearer {admin_token}"})

    client.post("/api/v1/orders",
            json={
                "dishes":[
                {
                "dish_name":"水煮青菜",
                "price":"10"
            },
            {
                "dish_name":"红烧肉",
                "price":"30"
            },
            ]
            },
            headers={
            "Authorization":f"Bearer {admin_token}"
        }       
            )
    client.post("/api/v1/orders",
            json={
                "dishes":[
                {
                "dish_name":"水煮青菜",
                "price":"10"
            },
            {
                "dish_name":"红烧肉",
                "price":"30"
            },
            ]
            },
            headers={
            "Authorization":f"Bearer {admin_token}"
        }       
            )
    resp = client.get("/api/v1/orders",
        query_string={
            "page":1,
            "per_page":10
        },
        headers={
            "Authorization":f"Bearer {admin_token}"
        }           
        )
    assert resp.status_code==200
    assert resp.json["total"]>=1
    
# 测试用例6：获取某一用户所有订单

def test_get_my_orders_success(client,admin_token):
     # 先创建菜品（确保数据库中有这些菜）
    client.post("/api/v1/dishes", json={
        "dish_name": "水煮青菜",
        "price": "10",
        "dish_number": "100"
    }, headers={"Authorization": f"Bearer {admin_token}"})
    
    client.post("/api/v1/dishes", json={
        "dish_name": "红烧肉",
        "price": "10",
        "dish_number": "100"
    }, headers={"Authorization": f"Bearer {admin_token}"})

    client.post("/api/v1/orders",
            json={
                "dishes":[
                {
                "dish_name":"水煮青菜",
                "price":"10"
            },
            {
                "dish_name":"红烧肉",
                "price":"30"
            },
            ]
            },
        headers={
            "Authorization":f"Bearer {admin_token}"
        }        
            )
    client.post("/api/v1/orders",
            json={
                "dishes":[
                {
                "dish_name":"水煮青菜",
                "price":"10"
            },
            {
                "dish_name":"红烧肉",
                "price":"30"
            },
            ]
            },
        headers={
            "Authorization":f"Bearer {admin_token}"
        }        
            )
    resp = client.get("/api/v1/orders/my",
        query_string={
            "page":1,
            "per_page":10
        },
        headers={
            "Authorization":f"Bearer {admin_token}"
        }           
        )
    assert resp.status_code==200
    assert resp.json["total"]>=2
# 测试用例7：某一用户取消订单
def test_cancel_order_success(client,admin_token):
     # 先创建菜品（确保数据库中有这些菜）
    client.post("/api/v1/dishes", json={
        "dish_name": "水煮青菜",
        "price": "10",
        "dish_number": "100"
    }, headers={"Authorization": f"Bearer {admin_token}"})
    
    client.post("/api/v1/dishes", json={
        "dish_name": "红烧肉",
        "price": "10",
        "dish_number": "100"
    }, headers={"Authorization": f"Bearer {admin_token}"})

    create_resp = client.post("/api/v1/orders",
            json={
                "dishes":[
                {
                "dish_name":"水煮青菜",
                "price":"10"
            },
            {
                "dish_name":"红烧肉",
                "price":"30"
            },
            ]
            },
        headers={
            "Authorization":f"Bearer {admin_token}"
        }        
            )
    order_id = create_resp.json["id"]
    resp = client.patch(f"/api/v1/orders/{order_id}/cancel",
            json={
                "status":"cancelled"
            },
    headers={"Authorization": f"Bearer {admin_token}"}
            )
    assert resp.status_code ==200
    