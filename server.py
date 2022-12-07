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
channels = {}
emojis = {
    "[happy]": "\U0001F604",
    "[laugh]": "\U0001F602",
    "[sad]": "\U0001F641",
    "[angry]": "\U0001F620",
    "[gross]": "\U0001F922",
    "[cowboy]": "\U0001F920",
    "[party]": "\U0001F973",
    "[love]": "\U0001F497",
    "[wave]": "\U0001F44B",
}

print(f"Server running at {ip}:{port}!")

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
            elif message["command"] == "msg_ch":
                for add in channels[message["channel"]]:
                    host_sock.sendto(str.encode(json.dumps(message)), add)
            elif message["command"] == "add":
                handles = message["handles"]
                message.pop("handles")
                for handle in handles:
                    host_sock.sendto(str.encode(json.dumps(message)), users[handle])
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
        elif command == "msg" or command == "all" or command == "msg_ch":
            if client_addr not in list(users.values()):
                msg_to_client["command"] = "error"
                msg_to_client["message"] = "Error: You must be registered with a handle or alias first."
            elif command == "msg" and data["handle"] not in list(users.keys()):
                msg_to_client["command"] = "error"
                msg_to_client["message"] = "Error: Handle or alias not found."
            elif command == "msg" and data["handle"] == get_sender_handle(client_addr):
                msg_to_client["command"] = "error"
                msg_to_client["message"] = "Error: You are trying to send a message to yourself."
            elif command == "msg_ch" and data["channel"] not in list(channels.keys()):
                msg_to_client["command"] = "error"
                msg_to_client["message"] = "Error: Channel not found."
            elif command == "msg_ch" and client_addr not in channels[data["channel"]]:
                msg_to_client["command"] = "error"
                msg_to_client["message"] = "Error: You are not a member of this channel."
            else:
                if command == "msg":
                    msg_to_client["handle"] = data["handle"]
                elif command == "msg_ch":
                    msg_to_client["channel"] = data["channel"]
                    msg_to_client["sender"] = get_sender_handle(client_addr)
                msg_to_client["message"] = data["message"]

                for emoji, code in emojis.items():
                    msg_to_client["message"] = msg_to_client["message"].replace(emoji, code)

                msg_to_client["sender"] = get_sender_handle(client_addr)
        elif command == "leave":
            if client_addr in list(users.values()):
                removed = users.pop(get_sender_handle(client_addr))

        elif command == "ch":
            if client_addr not in list(users.values()):
                msg_to_client["command"] = "error"
                msg_to_client["message"] = "Error: You must be registered with a handle or alias first."
            elif data["channel"] in list(channels.keys()):
                msg_to_client["command"] = "error"
                msg_to_client["message"] = "Error: Creating channel failed. Channel name already exists."
            else:
                channels[data["channel"]] = [client_addr]
                msg_to_client["channel"] = data["channel"]
        elif command == "add":
            if data["channel"] not in list(channels.keys()):
                msg_to_client["command"] = "error"
                msg_to_client["message"] = "Error: Channel does not exist."
            else:
                to_add = data["handles"].split()
                ctr = 0
                for handle in to_add:
                    if handle not in list(users.keys()):
                        msg_to_client["command"] = "error"
                        msg_to_client["message"] = "Error: One or more handles or aliases do not exist."
                        break
                    else:
                        ctr = ctr + 1
                        if users[handle] not in channels[data["channel"]]:
                            channels[data["channel"]].append(users[handle])
                if ctr == len(to_add):
                    msg_to_client["channel"] = data["channel"]
                    msg_to_client["handles"] = to_add
        elif command == "leave_ch":
            if data["channel"] not in list(channels.keys()):
                msg_to_client["command"] = "error"
                msg_to_client["message"] = "Error: Channel does not exist."
            elif client_addr not in channels[data["channel"]]:
                msg_to_client["command"] = "error"
                msg_to_client["message"] = "Error: You are not a member of this channel."
            else:
                channels[data["channel"]].remove(client_addr)
                msg_to_client["channel"] = data["channel"]

        messages.put((msg_to_client, client_addr))

def get_sender_handle(client_addr):
    return list(users.keys())[list(users.values()).index(client_addr)]

t1 = threading.Thread(target=receive)
t2 = threading.Thread(target=send_response)

t1.start()
t2.start()