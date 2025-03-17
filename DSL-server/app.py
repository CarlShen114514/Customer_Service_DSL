from flask import Flask, request, redirect, url_for, session, render_template_string, jsonify
from threading import Timer, Lock
import threading
import yaml
import os
#os.chdir("/home/carl/DSL-server")
import sys

current_path = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(current_path)
import server.db_management as db
from server.DFA import DFA
from WebUI.webUI_server import start_webUI

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

current_script = config['script']['current_script']
server_host = config['server']['host']
server_port = config['server']['port']

app = Flask(__name__)
app.secret_key = os.urandom(24)  # 生成一个随机密钥


lock = Lock()
dfa_group: dict[str, DFA] = {}
user_timers: dict[str, Timer] = {}

def reset_timer(username):
    """
    重置用户的计时器。对于每一个用户，上线或有操作时刷新timer的5min倒计时
    """
    if username in user_timers:
        user_timers[username].cancel()
    timer = Timer(300, set_user_offline, args=[username])  # 5分钟（300秒）计时器
    user_timers[username] = timer
    timer.start()

def set_user_offline(username):
    """
    在用户登出或者计时器超时的情况下将用户设置为离线状态，删除计时器以及此用户对应的DFA
    """
    with lock:
        if username in user_timers:
            print(f'User {username} is set to offline due to inactivity.')
            user_timers.pop(username, None)
            if username in dfa_group:
                del dfa_group[username]

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if db.add_user(username, password):
        return jsonify({'status': 'success'})
    else: 
        return jsonify({'status': '注册失败：用户名已存在'}), 400

@app.route('/login', methods=['POST'])
def login():
    """
    用于相应用户的登录请求，并为新登录的用户创建一个对应的DFA用于客服对话
    """
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if username in user_timers:
        return jsonify({'status': '用户已在线'}), 401

    user = db.get_user(username, password)
    
    if user:
        session['username'] = username
        with lock:
            reset_timer(username)
            dfa_group[username] = DFA(current_script)
            hello_info = dfa_group[username].get_state_hint()
            #print(hello_info)
        response = {
            'status': 'success',
            'hello_info': hello_info
        }
        return jsonify(response)
    else:
        return jsonify({'status': '用户不存在或密码错误'}), 401

@app.route('/logout', methods=['POST'])
def logout():
    """
    用于相应用户的登出请求，将此用户的timer和DFA进行销毁
    """
    data = request.json
    username = data['username']
    session.pop('username', None)
    set_user_offline(username)
    return jsonify({'message': 'Logout successful'})

@app.route('/chat', methods=['POST'])
def chat():
    """
    用于相应用户的聊天请求，将用户输入提取提供给此用户对应的DFA，让DFA发生状态转移并给出对应输出。
    给用户返回对应的DFA输出。
    """
    data = request.json
    username = data['username']
    message:str = data['message']
    if username in user_timers:
        with lock:
            reset_timer(username)
            #print(dfa_group[username].current.state, dfa_group[username].current.operation_index)
            reply = dfa_group[username].state_transition(message.strip())
            running = dfa_group[username].current.is_running
        if not running:
            with lock:
                bye_msg = dfa_group[username].exit.exec(dfa_group[username].current) #当用户结束会话时获取DFA的结束相应
                reply.extend(bye_msg)
        response = {
            'status': 'success',
            'running': running,
            'reply': reply,
            'bye': len(reply) - len(bye_msg) if not running else 0
        }
        #print(reply)
        return jsonify(response)
    else:
        response = {
            'status': '用户未登录或会话已超时'
        }
        return jsonify(response), 401

def start_pywebio_server():
    start_webUI()

if __name__ == '__main__':
    '''
    pywebio_thread = threading.Thread(target=start_pywebio_server)
    pywebio_thread.daemon = True
    pywebio_thread.start()
    '''
    app.run(host=server_host, port=server_port, threaded=True, debug=True)

    