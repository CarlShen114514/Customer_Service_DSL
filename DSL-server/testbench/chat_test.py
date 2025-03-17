import unittest
import os
os.chdir("/home/carl/DSL-server")
import sys
sys.path.append('/home/carl/DSL-server')

from app import app, DFA, current_script, set_user_offline
from flask import json

class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.app.post('/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        # 创建一个 DFA 实例并添加到 dfa_group

    def tearDown(self):
        # 清理测试用户和 DFA 实例
        set_user_offline('testuser')

    def test_chat(self):
        # 发送聊天请求
        response = self.app.post('/chat', data=json.dumps({
            'username': 'testuser',
            'message': 'Hello'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('reply', data)
        self.assertIsInstance(data['reply'], list)

if __name__ == '__main__':
    unittest.main()