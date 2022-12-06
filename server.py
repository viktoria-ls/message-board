import socket
import json
import queue
import threading

host_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ip = "127.0.0.1"
port = 12345
buffer_size = 1024
host_sock.bind((ip, port))

messages = queue.Queue()
users = {}

def send_response():
    while True:
        while not messages.empty():
            message, ip_port = messages.get()
            if message["command"] == "msg":
                host_sock.sendto(str.encode(json.dumps(message)), users[message["handle"]])
                host_sock.sendto(str.encode(json.dumps(message)), ip_port)
            elif message["command"] == "all":
                for add in list(users.values()):
                    host_sock.sendto(str.encode(json.dumps(message)), add)
            else:
                host_sock.sendto(str.encode(json.dumps(message)), ip_port)

def receive():
    running = True
    while running:
        print("Waiting for client...")
        data, client_addr = host_sock.recvfrom(buffer_size)
        data = json.loads(data.decode())
        print(data)

        msg_to_client = {}
        command = data["command"]
        msg_to_client["command"] = command

        if command == "register":
            if data["handle"] in list(users.keys()):
                msg_to_client["command"] = "error"
                msg_to_client["message"] = "Error: Registration failed. Handle or alias already exists."
            else:
                users[data["handle"]] = client_addr
                msg_to_client["handle"] = data["handle"]
        elif command == "msg" or command == "all":
            if client_addr not in list(users.values()):
                msg_to_client["command"] = "error"
                msg_to_client["message"] = "Error: You must be registered with a handle or alias first."
            elif command == "msg" and data["handle"] not in list(users.keys()):
                msg_to_client["command"] = "error"
                msg_to_client["message"] = "Error: Handle or alias not found."
            else:
                if command == "msg":
                    msg_to_client["handle"] = data["handle"]
                msg_to_client["message"] = data["message"]
                msg_to_client["sender"] = list(users.keys())[list(users.values()).index(client_addr)]
        elif command == "leave":
            if client_addr in list(users.values()):
                users.pop(list(users.keys())[list(users.values()).index(client_addr)])

        messages.put((msg_to_client, client_addr))

t1 = threading.Thread(target=receive)
t2 = threading.Thread(target=send_response)

t1.start()
t2.start()