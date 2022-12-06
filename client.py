import socket
import json
import queue
import threading

client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ip = "127.0.0.1"
port = 0
buffer_size = 1024
client_sock.bind((ip, port))

messages = queue.Queue()
server_ip = None
server_port = None
handle = ""

commands_params = {
    "join": ["server_ip_add", "server_port"],
    "leave": [],
    "register": ["handle"],
    "all": ["message"],
    "msg": ["handle", "message"],
    "?": []
}

update = ""

def update_board(message):
    update = message
    print(update)

def handle_reply():
    while True:
        message = client_sock.recvfrom(buffer_size)
        messages.put(message)
        while not messages.empty():
            global handle
            
            data, server_addr = messages.get()
            data = json.loads(data.decode())
            # print(f"RECEIVING >> {data}")
            command = data["command"]

            if command == "join":
                update_board("Connection to the Message Board Server is successful!")
            elif command == "leave":
                update_board("Connection closed. Thank you!")
            elif command == "register":
                update_board(f"Welcome {data['handle']}!")
                handle = data["handle"]
            elif command == "all":
                update_board(f"{data['sender']}: {data['message']}")
            elif command == "msg":
                if data["sender"] == handle:
                    update_board(f"(To {data['handle']}): {data['message']}")
                else:
                    update_board(f"(From {data['sender']}): {data['message']}")

def send_command(message):
    global server_ip
    global server_port

    encoded_msg = str.encode(json.dumps(message))
    # print(f"SENDING >> {encoded_msg}")

    try:
        server_port = int(server_port)
        client_sock.sendto(encoded_msg, (server_ip, server_port))
    except:
        server_ip = None
        server_port = None
        update_board("Error: Connection to the Message Board Server has failed! Please check IP Address and Port Number.")   

def get_input():
    global server_ip
    global server_port
    global handle
    
    running = True
    while running:
        user_input = input().strip()
        msg_to_server = {}
        command = user_input.partition(" ")[0]

        # Command doesn't start with '/'
        if not command.startswith('/'):
            update_board("Error: Command not found. Command must start with '/'.")
            continue

        command = command.lstrip('/')

        # Command doesn't exist
        if command not in list(commands_params.keys()):
            update_board("Error: Command not found.")
            continue

        msg_to_server["command"] = command
        params = user_input.split()[1:]

        if command == "msg":
            msg_to_server["handle"] = params[0]
            msg_to_server["message"] = " ".join(params[1:])
        elif command == "all":
            msg_to_server["message"] = " ".join(params)
        elif command == "?":
            update_board("Display all commands!!")
            continue
        elif command == "leave":
            if server_ip == None:
                update_board("Error: Disconnection failed. Please connect to the server first.")
            else:
                send_command(msg_to_server)
                server_ip = None
                server_port = None
                handle = ""
            continue
        # Sending command but not connected to server
        elif server_ip == None and command != "join":
            update_board("Error: Not connected to a server. Please connect to a server first.")
            continue

        else:
            # Number of inputted parameters is not allowable
            if len(params) != len(commands_params[command]):
                update_board("Error: Command parameters do not match or is not allowed.")
                continue

            for index, param in enumerate(commands_params[command]):
                msg_to_server[param] = params[index]
            if command == "join":
                if server_ip != None:
                    update_board("Error: You are already connected to a server. Leave first before joining another server.")
                    continue
                else:
                    server_ip = params[0]
                    server_port = params[1]
            elif command == "register":
                if handle != "":
                    update_board(f'Error: You are already registered under the handle/alias, "{handle}".')
                    continue

        send_command(msg_to_server)

t1 = threading.Thread(target=get_input)
t2 = threading.Thread(target=handle_reply)

t1.start()
t2.start()