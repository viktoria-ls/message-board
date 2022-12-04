import socket
import json

host_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
host = socket.gethostname()
port = 2468
buffer_size = 1024
host_sock.bind((host, port))

commands_params = {
    "join": [],
    "register": ["handle"],
    "all": ["message"],
    "msg": ["handle", "message"]
}

users = {}

def send_response(message, ip_port):
    if message["command"] == "msg":
        host_sock.sendto(str.encode(json.dumps(message)), users[message[handle]])
        host_sock.sendto(str.encode(json.dumps(message)), ip_port)
    elif message["command"] == "all":
        for add in users.values():
            host_sock.sendto(str.encode(json.dumps(message)), add)
    else:
        host_sock.sendto(str.encode(json.dumps(message)), ip_port)

running = True
while running:
    print("Waiting for client...")
    data, client_addr = host_sock.recvfrom(buffer_size)
    data = json.loads(data.decode())
    print(data)

    msg_to_client = data

    if data["command"] == "register":
        if data["handle"] in list(users.keys()):
            msg_to_client["command"] = "error"
            msg_to_client["message"] = "Error: Registration failed. Handle or alias already exists."
        else:
            users[data["handle"]] = client_addr
    elif data["command"] == "msg":
        if data["handle"] not in list(users.keys()):
            msg_to_client["command"] = "error"
            msg_to_client["message"] = "Error: Handle or alias not found."
    elif data["command"] == "all":
        msg_to_client["sender"] = list(users.keys())[list(users.values()).index(client_addr)]

    send_response(msg_to_client, client_addr)