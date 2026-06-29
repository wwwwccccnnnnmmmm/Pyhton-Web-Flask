from flask import Flask

app = Flask(__name__)

@app.route("/health",methods=["GET"])
def health():
    
    return {"status":"OK","service":"FlaskAPI"}


if __name__ =='__main__':
    app.run(debug=True,host="127.0.0.1",port=5000)