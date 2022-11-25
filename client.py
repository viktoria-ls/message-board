import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

host = socket.gethostname()
port = 2468

msg = "Test message"

s.sendto(msg, (host, port))