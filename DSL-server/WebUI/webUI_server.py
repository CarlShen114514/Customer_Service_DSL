import asyncio
import requests
from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import defer_call, info as session_info, run_async, run_js, set_env
import time

MAX_MESSAGES_CNT = 10 ** 4

URL = 'http://127.0.0.1:5000'

chat_msgs = []

hello_msgs = []


async def refresh_msg(my_name):
    """send new message to current session"""
    global chat_msgs
    global hello_msgs

    last_idx = len(chat_msgs)
    while True:
        await asyncio.sleep(1.5)
        if len(hello_msgs) > 0:
            for msg in hello_msgs:
                chat_msgs.append(msg)
            hello_msgs = []

        for m in chat_msgs[last_idx:]:
            if m[0] == my_name + '的客服':
                await asyncio.sleep(1)
                put_markdown('`%s`: %s' % m, sanitize=True, scope='msg-box')

        # remove expired message
        if len(chat_msgs) > MAX_MESSAGES_CNT:
            chat_msgs = chat_msgs[len(chat_msgs) // 2:]

        last_idx = len(chat_msgs)


async def login():
    username = await input_group(('登陆：请输入用户名'), [
        input(name='usr'),
        actions(name='cmd', buttons=['确定', '注册', {'label': '退出', 'type': 'cancel'}])
    ], validate=lambda d: ('usr', '用户名不能为空') if d['cmd'] == '确定' and not d['usr'] else None)
    if username is None:
        run_js('window.close()') 
    if username['cmd'] == '注册':
        await registration()
        return await login()
   
    password = await input_group(('登陆：请输入密码'), [
        input(name='pwd'),
        actions(name='cmd', buttons=['登陆', {'label': '退出', 'type': 'cancel'}])
    ], validate=lambda d: ('pwd', '密码不能为空') if d['cmd'] == '登陆' and not d['pwd'] else None)
    if password is None:
        run_js('window.close()') 
    try:
        response = requests.post(f'{URL}/login', json={'username': username['usr'], 'password': password['pwd']})
        result = response.json()
        if result['status'] == 'success':
            toast("登陆成功！", duration=2)
            return (username['usr'], result['hello_info'])
        else:
            toast(result['status'], duration=2)
            return await login()
    except:
        toast("网络错误", duration=2)
        return await login()

async def registration():
    username = await input_group(('注册：请输入用户名'), [
        input(name='usr'),
        actions(name='cmd', buttons=['确定', {'label': '取消', 'type': 'cancel'}])
    ], validate=lambda d: ('usr', '用户名不能为空') if d['cmd'] == '确定' and not d['usr'] else None)
    if username is None:
        return
    password = await input_group(('注册：请输入密码'), [
        input(name='pwd'),
        actions(name='cmd', buttons=['提交', {'label': '退出', 'type': 'cancel'}])
    ], validate=lambda d: ('pwd', '密码不能为空') if d['cmd'] == '提交' and not d['pwd'] else None)
    if password is None:
        return
    response = requests.post(f'{URL}/register', json={'username': username['usr'], 'password': password['pwd']})
    result = response.json()
    if result['status'] == 'success':
        toast("注册成功！", duration=2)
    else:
        toast(result['status'], duration=2)

async def chat_page():

    global chat_msgs
    set_env(title="Customer Service")
    put_markdown(("## 欢迎使用客户服务系统"))

    (username, hello_info) = await login()
    
    put_scrollable(put_scope('msg-box'), height=300, keep_bottom=True)
    put_markdown('`📢`: 用户`%s`您好，很高兴为您服务' % (username), sanitize=True, scope='msg-box')
    refresh_task = run_async(refresh_msg(username))
    
    for msg in hello_info:
        hello_msgs.append((username + '的客服', msg))
    while True:
        data = await input_group(('发送消息'), [
            input(name='msg'),
            actions(name='cmd', buttons=['发送', {'label': '退出', 'type': 'cancel'}])
        ], validate=lambda d: ('msg', '消息不能为空') if d['cmd'] == '发送' and not d['msg'] else None)
        if data is None:
            break
        put_markdown('`%s`: %s' % (username, data['msg']), sanitize=True, scope='msg-box')
        chat_msgs.append((username, data['msg']))
        try:
            response = requests.post(f'{URL}/chat', json={'message': data['msg'], 'username': username})
            result = response.json()
            if not result['running']:
                for msg in result['reply'][result['bye']:]:
                    chat_msgs.append((username + '的客服', msg))
                break
            else:
                for msg in result['reply']:
                    chat_msgs.append((username + '的客服', msg))
            
        except:
            toast("网络错误", duration=2)
            break
    
    try:
        response = requests.post(f'{URL}/logout', json={'username': username})
    except:
        toast("网络错误", duration=2)
    await asyncio.sleep(3)
    refresh_task.close()
    toast("您已离线")
    #time.sleep(2)
    #run_js('window.close()') 

def start_webUI():
    start_server(chat_page, port=8080)

if __name__ == '__main__':
    start_server(chat_page, host='192.168.1.5', port=11451)