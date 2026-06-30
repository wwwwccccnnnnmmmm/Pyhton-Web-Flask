from flask import Flask
from config import Config

from app.api.v1.users import users_bp
from app.api.v1.auth import auth_bp

app = Flask(__name__)
app.config.from_object(Config)

# 注册蓝图
app.register_blueprint(users_bp)
app.register_blueprint(auth_bp)

@app.route("/health",methods=["GET"])
def health():
    return {"status":"OK","service":"FlaskAPI"}
 
    
if __name__ =='__main__':
    app.run(debug=True,host="127.0.0.1",port=5000)