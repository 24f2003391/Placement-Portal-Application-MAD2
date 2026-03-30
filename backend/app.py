from flask import Flask, jsonify,request
from flask_security import Security

from controller.models import db

app = Flask(__name__)
db.init_app(app)



if __name__ == '__main__':    
    app.run(debug=True)
