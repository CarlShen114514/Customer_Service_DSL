import sys
import asyncio
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from webUI import start_webUI, chat_page

def start_pywebio_server():
    start_webUI()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DSL-client")
        self.setGeometry(100, 100, 1280, 960)

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("http://localhost:8080"))  # PyWebIO 应用的 URL
        self.setCentralWidget(self.browser)

if __name__ == "__main__":
    # 启动 PyWebIO 服务器的线程
    pywebio_thread = threading.Thread(target=start_pywebio_server)
    pywebio_thread.daemon = True
    pywebio_thread.start()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())