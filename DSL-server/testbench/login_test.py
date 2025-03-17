import unittest
import sys
import os
os.chdir("..")
sys.path.append('/home/carl/DSL-server')
from app import app, set_user_offline
from flask import json

class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_login(self):
        response = self.app.post('/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', response.get_json()['status'])

    def test_login_wrong_password(self):
        response = self.app.post('/login', data=json.dumps({
            'username': 'testuser1',
            'password': 'wrongpassword'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 401)
        self.assertIn('用户不存在或密码错误', response.get_json()['status'])

    def test_login_already_exist(self):
        response = self.app.post('/login', data=json.dumps({
            'username': 'testuser',
            'password': 'wrongpassword'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 401)
        self.assertIn('用户已在线', response.get_json()['status'])

    def test_logout(self):
        self.app.post('/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        response = self.app.post('/logout', data=json.dumps({
            'username': 'testuser'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Logout successful', response.get_json()['message'])

    def test_stress(self):
        import time
        start_time = time.time()
        for i in range(1000):
            self.app.post('/login', data=json.dumps({
                'username': f'testuser{i}',
                'password': 'testpassword'
            }), content_type='application/json')
        end_time = time.time()
        print(f"Stress test completed in {end_time - start_time} seconds")

if __name__ == '__main__':
    unittest.main()