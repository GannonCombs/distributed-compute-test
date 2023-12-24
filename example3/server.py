import socket
import signal
import sys

interrupted = False

def process_data(data):
    # A simple processing function that squares the input integer
    return int(data) ** 2

def signal_handler(signal, frame):
    global interrupted
    interrupted = True

def update_load_balancer(load_balancer_address, action, server_port):
    update_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    update_socket.connect(load_balancer_address)
    message = f"{action}:{server_port}"
    update_socket.sendall(message.encode('utf-8'))
    update_socket.close()

def main():
    global interrupted

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Obtain the server's port number from the command line argument
    server_port = int(sys.argv[1])

    server_address = ('localhost', server_port)
    server_socket.bind(server_address)

    server_socket.listen(5)
    server_socket.setblocking(False)  # Set the socket to non-blocking mode

    # Register the server with the load balancer
    load_balancer_address = ('localhost', 20001)

    update_load_balancer(load_balancer_address, "register", server_port)


    print(f"Server is ready to accept connections on port {server_port}...")

    signal.signal(signal.SIGINT, signal_handler)

    while not interrupted:
        try:
            client_socket, client_address = server_socket.accept()
            print(f"Connection from: {client_address}")

            data = client_socket.recv(1024).decode('utf-8')
            print(f"Received data: {data}")

            result = process_data(data)

            client_socket.sendall(str(result).encode('utf-8'))
            client_socket.close()

        except socket.error as e:
            if not interrupted:
                continue
            else:
                update_load_balancer(load_balancer_address, "unregister", server_port)
                print("Exiting...")
                break

if __name__ == "__main__":
    main()
