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
    "msg": ["handle", "message"]
}

update = ""

def update_board(message):
    update = message
    print(update)

def handle_reply(message):
    print(message)

def send_command(message):
    encoded_msg = str.encode(json.dumps(message))
    print(f"SENDING >> {encoded_msg}")

    if server_ip is None and command != "join":
        update_board("Error: Not connected to a server. Please connect to a server first.")
    else:
        client_sock.sendto(encoded_msg, (server_ip, port))
        handle_reply(client_sock.recvfrom(buffer_size))

running = True
while running:
    user_input = input("Enter command: ").strip()
    msg_to_server = {}
    command = user_input.partition(" ")[0]

    # Command doesn't start with '/'
    if not command.startswith('/'):
        update_board("Error: Command not found. Command must start with '/'.")
    else:
        command = command.lstrip('/')
        # Command doesn't exist
        if command not in list(commands_params.keys()):
            update_board("Error: Command not found.")
        else:
            msg_to_server["command"] = command
            params = user_input.split()[1:]
            if command == "msg":
                msg_to_server["handle"] = params[0]
                msg_to_server["message"] = " ".join(params[1:])
            elif command == "all":
                msg_to_server["message"] = " ".join(params)
            elif command == "leave":
                if server_ip == None:
                    update_board("Error: Disconnection failed. Please connect to the server first.")
                else:
                    send_command(msg_to_server)
                    server_ip = None
                    port = None
                    handle = ""
                continue
            else:
                # Number of inputted parameters is not allowable
                if len(params) != len(commands_params[command]):
                    update_board("Error: Command parameters do not match or is not allowed.")
                else:
                    for index, param in enumerate(commands_params[command]):
                        msg_to_server[param] = params[index]
                    if command == "join":
                        server_ip = params[0]
                        port = int(params[1])
                        try:
                            send_command(msg_to_server)
                        except:
                            update_board("Error: Connection to the Message Board Server has failed! Please check IP Address and Port Number.")   
                        finally:
                            continue
                    elif command == "register":
                        handle = params[0]

    send_command(msg_to_server)