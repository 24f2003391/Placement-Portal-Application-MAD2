from flask import Flask, jsonify,request
from flask_security import Sec

app = Flask(__name__)

@app.route('/')
def home():
    data = request.get_json()
    print(data)
    a = data.get('a',0)
    b = data.get('b', 0)
    result = {'a+b': a+b, 'a-b': a-b, 'a*b': a*b, 'a/b': a/b}
    return jsonify(result)

if __name__ == '__main__':    
    app.run(debug=True)
