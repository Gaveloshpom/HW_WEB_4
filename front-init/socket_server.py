import socket

def main():
    host = socket.gethostname()
    port = 5000
    server_socket = socket.socket()
    server_socket.bind((host, port))
    server_socket.listen()

    conn, address = server_socket.accept()
    print(f"Connection from: {address}")
    while True:
        data = conn.recv(100).decode()
        if not data:
            break
        print(f"Received: {data}")
        message = input("Input message: ")
        conn.send(message.encode())
    conn.close()
    server_socket.close()

if __name__ == "__main__":
    main()
    