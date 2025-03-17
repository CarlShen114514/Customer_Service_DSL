from locust import HttpUser, TaskSet, task, between
import uuid

class UserBehavior(TaskSet):
    def on_start(self):
        """
        在测试开始时执行登录操作
        """
        self.username = f"testuser_{uuid.uuid4()}"
        self.register()
        self.login()

    def register(self):
        response = self.client.post("/register", json={
            "username": self.username,
            "password": "testpassword"
        })

    def login(self):
        response = self.client.post("/login", json={
            "username": self.username,
            "password": "testpassword"
        })

    @task(1)
    def chat(self):
        """
        模拟用户发送消息
        """
        response = self.client.post("/chat", json={
            "username": self.username,
            "message": "Hello, how can I help you?"
        })
        if response.status_code == 401:
            self.login()


class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)  # 每个任务之间等待1到5秒

if __name__ == "__main__":
    import os
    os.system("locust -f pressure_test.py")