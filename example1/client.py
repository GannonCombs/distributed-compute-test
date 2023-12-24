import socket

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = ('localhost', 10000)
    client_socket.connect(server_address)

    data_to_send = input("Enter the data to send to the server: ")

    client_socket.sendall(data_to_send.encode('utf-8'))

    result = client_socket.recv(1024).decode('utf-8')
    print(f"Received result from the server: {result}")

    client_socket.close()

if __name__ == "__main__":
    main()
