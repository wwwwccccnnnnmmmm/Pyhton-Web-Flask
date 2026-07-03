# 餐饮管理系统（Flask学习项目）
目的：通过实现多个API 以此实现逆向学习Flask
## 1.项目目标
实现一个简单的餐饮管理系统，包含用户认证、菜品管理、订单管理等功能

## 2.技术栈
python3.X
Flask
Flask-sqlalchemy（ORM映射）
pyJWT(用户认证)
SQLite（数据库）

## 3.功能开发路线图

### 3.1搭建环境：
    [√] 3.1.1 虚拟环境配置
    [√] 3.1.2 安装依赖
    [√] 3.1.3 搭建Flask框架

### 3.2用户认证功能实现
    [√] 3.2.1 登录功能 POST /auth/login
    [√] 3.2.2 注册功能 POST /auth/register
    [√] 3.2.3 登出功能 GET /auth/logout
    [] 3.2.4 个人资料 GET /auth/me
    
### 3.3 菜品管理功能实现
    [√] 3.3.1 获取菜品 GET /dishes/<id>
    [√] 3.3.2 增加菜品 POST /dishes
    [√] 3.3.3 删除菜品 DELETE /dishes/<id>
    [√] 3.3.4 修改菜品 PATCH /dishes/<id>
    [] 3.3.5 获取所有菜品 GET /dishes

### 3.4 订单管理功能实现
    [] 3.4.1 获取订单 GET /orders/<id>
    [] 3.4.2 新建订单 POST /orders
    [] 3.4.3 删除订单 DELETE /orders/<id>
    [] 3.4.4 获取订单详情 GET /orders/<id>
    [] 3.4.5 获取所有订单 GET /orders

### 3.5 用户管理功能实现
    [√] 3.5.1 获取用户 GET /users/<id>
    [√] 3.6.2 新建用户 POST /users
    [√] 3.5.3 删除用户 DELETE /users/<id>
    [√] 3.5.4 修改用户 PATCH /users/<id>
    [] 3.5.5 获取所有用户 GET /users
        