import socket

def process_data(data):
    # A simple processing function that reverses the input string
    return data[::-1]

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = ('localhost', 10000)
    server_socket.bind(server_address)

    server_socket.listen(5)

    print("Server is ready to accept connections...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection from: {client_address}")

        data = client_socket.recv(1024).decode('utf-8')
        print(f"Received data: {data}")

        result = process_data(data)

        client_socket.sendall(result.encode('utf-8'))
        client_socket.close()

if __name__ == "__main__":
    main()
