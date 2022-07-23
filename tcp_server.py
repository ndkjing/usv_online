import re
import socket
import server_config
import json
import time
import requests
import threading


def singleton(cls):
    _instance = {}

    def _singleton(*args, **kargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kargs)
        return _instance[cls]
    return _singleton


@singleton
class TcpServer:
    def __init__(self):
        self.bind_ip = server_config.tcp_server_ip  # 监听所有可用的接口
        self.bind_port = server_config.tcp_server_port  # 非特权端口号都可以使用
        # AF_INET：使用标准的IPv4地址或主机名，SOCK_STREAM：说明这是一个TCP服务器
        self.tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 服务器监听的ip和端口号
        self.tcp_server_socket.bind((self.bind_ip, self.bind_port))
        print("[*] Listening on %s:%d" % (self.bind_ip, self.bind_port))
        self.tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        # 最大连接数
        self.tcp_server_socket.listen(128)
        # 是否有链接上
        self.b_connect = 0
        self.client = None
        self.client_dict={}  # {船号:client}

    def wait_connect(self):
        # 等待客户连接，连接成功后，将socket对象保存到client，将细节数据等保存到addr
        client, addr = self.tcp_server_socket.accept()
        print("客户端的ip地址和端口号为:", addr)
        self.b_connect = 1
        self.client = client

    def start_server(self):
        while True:
            # 等待客户连接，连接成功后，将socket对象保存到client，将细节数据等保存到addr
            client, addr = self.tcp_server_socket.accept()
            print("客户端的ip地址和端口号为:", addr)
            print('time:', time.time())
            # 代码执行到此，说明客户端和服务端套接字建立连接成功
            print("[*] Acception connection from %s:%d" % (addr[0], addr[1]))
            client_handler = threading.Thread(target=self.handle_client, args=(client,))
            # 子线程守护主线程
            client_handler.setDaemon(True)
            client_handler.start()
            time.sleep(0.5)

    # 客户处理线程
    def handle_client(self, client):
        # 这个while可以不间断的接收客户端信息
        while True:
            recv_data = client.recv(1024)
            # client_socket.send("hi~".encode())
            # recv_data = client_socket.recv(1024)
            # print("[*] Received: %s" % recv_data)
            # 向客户端返回数据
            if recv_data:
                recv_content = recv_data.decode("gbk")
                ship_id_list = re.findall('[AB](\d+)',recv_content)
                if len(ship_id_list)>0:
                    ship_id = int(ship_id_list[0])
                    print('ship_id',ship_id)
                    if not ship_id in self.client_dict:
                        self.client_dict.update({ship_id:client})
                        print('self.client_dict',self.client_dict)
                    print("接收客户端的数据:", recv_content)

    def close(self):
        self.tcp_server_socket.close()

    def write_data(self,ship_id,data):
        print('ship_id', ship_id,self.client_dict)
        if ship_id in self.client_dict:
            print('ship_id',ship_id)
            self.client_dict.get(ship_id).send(data.encode())

def te_():
    while True:
        for i in range(4):
            obj.write_data(i,str(i))
        time.sleep(1)

if __name__ == '__main__':
    obj = TcpServer()
    te_handler = threading.Thread(target=te_)
    # 子线程守护主线程
    te_handler.setDaemon(True)
    te_handler.start()
    obj.start_server()
