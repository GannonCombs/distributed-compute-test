import socket
import signal

def signal_handler(signal, frame):
    global interrupted
    interrupted = True

def main():
    global interrupted

    load_balancer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    load_balancer_address = ('localhost', 20000)
    load_balancer_socket.bind(load_balancer_address)

    load_balancer_socket.listen(5)
    load_balancer_socket.setblocking(False)  # Set the socket to non-blocking mode

    print("Load balancer is ready to accept connections...")

    server_ports = [10001, 10002, 10003]  # List of available server ports
    server_index = 0

    signal.signal(signal.SIGINT, signal_handler)

    interrupted = False

    while not interrupted:
        try:
            client_socket, client_address = load_balancer_socket.accept()
            print(f"Connection from: {client_address}")

            data = client_socket.recv(1024).decode('utf-8')
            print(f"Received data: {data}")

            # Distribute tasks to servers in a round-robin fashion
            server_port = server_ports[server_index]
            server_index = (server_index + 1) % len(server_ports)

            # Connect to the selected server and forward the data
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = ('localhost', server_port)
            server_socket.connect(server_address)
            server_socket.sendall(data.encode('utf-8'))

            # Receive the result from the server and forward it to the client
            result = server_socket.recv(1024).decode('utf-8')
            print(f"Received result from the server: {result}")

            client_socket.sendall(result.encode('utf-8'))

            server_socket.close()
            client_socket.close()

        except socket.error as e:
            if not interrupted:
                continue
            else:
                print("Exiting...")
                break

if __name__ == "__main__":
    main()
