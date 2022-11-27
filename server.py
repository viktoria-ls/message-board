import socket

host_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

host = socket.gethostname()
port = 2468
buffer_size = 1024

host_sock.bind((host, port))

running = True
while running:
    print("Waiting for client...")
    data, client_addr = host_sock.recvfrom(buffer_size)
    if data.lower() == "hello":
        reply = str.encode("Hello right back at ya!")
    else:
        reply = str.encode("Not even a hello?")
    print(f"Message from [{client_addr}]: {data}")
    host_sock.sendto(reply, client_addr)