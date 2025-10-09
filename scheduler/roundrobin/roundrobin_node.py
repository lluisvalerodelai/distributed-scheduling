import socket

host = '10.0.0.9'
port = '42069'

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((host, port))

    s.sendall("hi".encode())
    response = s.recv(1024).decode()
    print(response)
