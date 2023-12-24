import socket

def main():
    load_balancer_address = ('localhost', 20000)

    while True:
        data_to_send = input("Enter the data to send to the server (type 'exit' to quit): ")
        if data_to_send.lower() == 'exit':
            break

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(load_balancer_address)
        
        client_socket.sendall(data_to_send.encode('utf-8'))

        result = client_socket.recv(1024).decode('utf-8')
        print(f"Received result from the server: {result}")

        client_socket.close()

if __name__ == "__main__":
    main()
