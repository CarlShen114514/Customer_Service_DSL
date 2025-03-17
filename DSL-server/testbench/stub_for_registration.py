import requests

BASE_URL = 'http://127.0.0.1:5000'

def test_register():
    url = f'{BASE_URL}/register'
    data = {
        'username': 'newuser',
        'password': 'newpassword'
    }
    response = requests.post(url, json=data)
    print('Register Response:', response.status_code, response.json())

def test_login():
    url = f'{BASE_URL}/login'
    
    # 正确的用户名和密码
    data = {
        'username': 'newuser',
        'password': 'newpassword'
    }
    response = requests.post(url, json=data)
    print('Login Response (correct):', response.status_code, response.json())
    
    # 错误的密码
    data = {
        'username': 'newuser',
        'password': 'wrongpassword'
    }
    response = requests.post(url, json=data)
    print('Login Response (wrong password):', response.status_code, response.json())

def test_logout():
    url = f'{BASE_URL}/logout'
    response = requests.post(url)
    print('Logout Response:', response.status_code, response.json())

if __name__ == '__main__':
    test_register()
    test_login()
    test_logout()
