import socket # модуль для работы с сетевыми сокетами
import threading # модуль для работы с потоками

class GameClient:
    def __init__(self, host='192.168.1.16', port=33333):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.buffer = b''
        self.lock = threading.Lock()

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            # Получаем приветственное сообщение
            welcome = self.recv_line()
            print("Server:", welcome)
            return True
        except Exception as e:
            print("Connection failed:", e)
            return False


# Метод для отправки команды на сервер и получения ответа
    def send_command(self, cmd):
        """Отправить команду и вернуть ответ (строка)"""
        if not self.connected:
            return None
        try:
            self.socket.sendall((cmd + '\n').encode())
            return self.recv_line()
        except Exception as e:
            print("Send error:", e)
            self.connected = False
            return None

    def recv_line(self):
        """Получить одну строку ответа (до \r\n)"""
        while b'\n' not in self.buffer:
            data = self.socket.recv(1024)
            if not data:
                self.connected = False
                return None
            self.buffer += data
        line, self.buffer = self.buffer.split(b'\n', 1)
        return line.decode().strip('\r')