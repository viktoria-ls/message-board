import socket
import json

# client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# buffer_size = 1024

# # this is server data that we want to connect to
# # should be inputted by client user
# host_ip = socket.gethostbyname(socket.gethostname())
# port = 2468

# print("client host: " + host_ip)

# msg = input("Message: ")
# encoded_msg = str.encode(msg)

# client_sock.sendto(encoded_msg, (host_ip, port))
# reply = client_sock.recvfrom(buffer_size)
# print(reply)

commands_params = {
    "join": ["server_ip_add", "port"],
    "leave": [],
    "register": ["handle"],
    "all": ["message"],
    "msg": ["handle", "message"]
}

server_ip = None
port = None
running = True

# Refactor to handle errors in server app not here
while running:
    user_input = input("Enter command: ").strip()
    msg_to_server = {}
    msg_to_server["command"] = "error"
    command = user_input.partition(" ")[0]

    # Command doesn't start with '/'
    if not command.startswith('/'):
        msg_to_server["message"] = "Command not found. Command must start with '/'."
    else:
        command = command.lstrip('/')
        # Command doesn't exist
        if command not in list(commands_params.keys()):
            msg_to_server["message"] = "Command not found."
        else:
            # Attempting to send command when not connected to a server
            if server_ip is None and command != "join":
                msg_to_server["message"] = "Not connected to a server. Please connect to a server first."
            else:
                msg_to_server["command"] = command
                params = user_input.split()[1:]
                if command == "msg":
                    msg_to_server["handle"] = params[0]
                    msg_to_server["message"] = " ".join(params[1:])
                elif command == "all":
                    msg_to_server["message"] = " ".join(params)
                elif command == "leave":
                    server_ip = None
                    port = None
                else:
                    # Number of inputted parameters is not allowable
                    if len(params) != len(commands_params[command]):
                        msg_to_server["message"] = "Command parameters do not match or is not allowed."
                    else:
                        for index, param in enumerate(commands_params[command]):
                            msg_to_server[param] = params[index]
                        if command == "join":
                            server_ip = params[0]
                            port = params[1]
                            # connect to server here and add error message
                            print("Pretend we're connected to a server!")

    print(msg_to_server)
    # encode
    # send to server
    # receive response from server (in JSON)
    # display response