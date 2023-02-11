import socket

def main():
    host = socket.gethostname()
    port = 5000

    client_socket = socket.socket()
    client_socket.connect((host, port))
    message = input("Input message: ")
    while message.lower().encode() != "exit":
        client_socket.send(message.encode())
        server_message = client_socket.recv(100).decode()
        print(f"Received message: {server_message}")
        message = input("Input message: ")
    client_socket.close()

if __name__ == "__main__":
    main()
