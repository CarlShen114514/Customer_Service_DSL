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

    def test_register(self):
        response = self.app.post('/register', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', response.get_json()['status'])

    def test_register_existing_user(self):
        response = self.app.post('/register', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('注册失败：用户名已存在', response.get_json()['status'])

    def test_stress(self):
        import time
        start_time = time.time()
        for i in range(1000):
            self.app.post('/register', data=json.dumps({
                'username': f'testuser{i}',
                'password': 'testpassword'
            }), content_type='application/json')
        end_time = time.time()
        print(f"Register test completed in {end_time - start_time} seconds")

if __name__ == '__main__':
    unittest.main()