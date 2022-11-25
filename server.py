import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

host = socket.gethostname()
port = 2468

s.bind((host, port))

while True:
    print("Waiting for client...")
    data, client_addr = s.recvfrom(1024)
    print(f"Message from [{client_addr}]: {data}")