from flask import Flask, request, redirect, url_for, session, render_template_string, jsonify
app = Flask(__name__)
app.secret_key = 'thisisakey'
@app.route('/register', methods=['POST'])
def register():
    
    return jsonify({'message': 'User registered successfully'})

@app.route('/login', methods=['POST'])
def login():
    hello = ['这是一个测试桩','This is a test stub']
    data = {
        'status': 'success',
        'hello_info': hello
    }
    return jsonify(data)

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return jsonify({'status': 'success'})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message:str = data['message']
    message = message.replace("你", "as;dfasdfaasdfa")
    message = message.replace("我", "你")
    message = message.replace("as;dfasdfaasdfa", "我")
    # 简单回显用户消息
    response = {
        'status': 'success',
        'running': True,
        'reply': [message],
        'bye': 0
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,threaded=True, debug=True)