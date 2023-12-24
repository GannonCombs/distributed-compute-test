import socket
import signal
import threading
import sys

def signal_handler(signal, frame):
    global interrupted
    interrupted = True
    print("Exiting...")
    sys.exit(0)

def listen_for_updates():
    global server_ports

    registration_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    registration_address = ('localhost', 20001)
    registration_socket.bind(registration_address)
    registration_socket.listen(5)

    while not interrupted:
        try:
            server_socket, server_address = registration_socket.accept()

            #This data comes in the format {action}:{server_port}
            #The action should be "register" or "unregister"
            data = server_socket.recv(1024).decode('utf-8').strip()
            print(f"Received registration data: {data}")
            if not data or ':' not in data:  # Handle empty or bad data
                server_socket.close()

            action, server_port = data.split(':')
            server_port = int(server_port)

            if action == 'register':
                register_server(server_port)
            elif action == 'unregister':
                unregister_server(server_port)

            server_socket.close()
            
        except socket.error as e:
            if not interrupted:
                continue
            else:
                print("Exiting...")
                break

def register_server(server_port):
    server_ports.add(server_port)
    print(f"Registered server on port {server_port}")

def unregister_server(server_port):
    if server_port in server_ports:
        server_ports.remove(server_port)
        print(f"Unregistered server on port {server_port}")
    else:
        print(f"Server on port {server_port} not found")

def main():
    global interrupted
    global server_ports

    load_balancer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    load_balancer_address = ('localhost', 20000)
    load_balancer_socket.bind(load_balancer_address)

    load_balancer_socket.listen(5)
    load_balancer_socket.setblocking(False)  # Set the socket to non-blocking mode

    print("Load balancer is ready to accept connections...")

    server_ports = set()  # Initialize an empty set for server_ports
    server_index = 0

    signal.signal(signal.SIGINT, signal_handler)

    # Start the update listener in a separate thread
    update_registration_thread = threading.Thread(target=listen_for_updates)
    update_registration_thread.start()

    interrupted = False

    while not interrupted:
        try:
            client_socket, client_address = load_balancer_socket.accept()
            print(f"Connection from: {client_address}")

            data = client_socket.recv(1024).decode('utf-8')
            print(f"Received data: {data}")

            if server_ports:
                server_ports_list = list(server_ports)  # Convert the set to a list

                # Distribute tasks to servers in a round-robin fashion
                server_port = server_ports_list[server_index]
                server_index = (server_index + 1) % len(server_ports_list)

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
            else:
                print("No servers available")
                result = "No servers available"
                client_socket.sendall(result.encode('utf-8'))

            client_socket.close()

        except socket.error as e:
            if not interrupted:
                continue
            else:
                update_registration_thread.join()
                load_balancer_socket.close()
                print("Exiting...")
                break


if __name__ == "__main__":
    main()
