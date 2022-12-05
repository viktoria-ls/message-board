import socket
import json

client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
buffer_size = 1024
server_ip = None
port = None
handle = ""

commands_params = {
    "join": ["server_ip_add", "port"],
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

def handle_reply(message):
    global handle
    data, server_addr = message
    data = json.loads(data.decode())
    print(f"RECEIVING >> {data}")
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
    global port

    encoded_msg = str.encode(json.dumps(message))
    # print(f"SENDING >> {encoded_msg}")

    try:
        port = int(port)
        client_sock.sendto(encoded_msg, (server_ip, port))
    except:
        server_ip = None
        port = None
        update_board("Error: Connection to the Message Board Server has failed! Please check IP Address and Port Number.")   
    else:
        reply = client_sock.recvfrom(buffer_size)
        handle_reply(reply)

running = True
while running:
    user_input = input("Enter command: ").strip()
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
            port = None
            handle = ""
        continue
    # Sending command but not connected to server
    elif server_ip is None and command != "join":
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
                port = params[1]
        elif command == "register":
            if handle != "":
                update_board(f'Error: You are already registered under the handle/alias, "{handle}".')
                continue

    send_command(msg_to_server)