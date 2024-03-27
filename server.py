import socket
import threading

SERVER = '127.0.0.1'
PORT = 12345
ADDR = (SERVER, PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clients = []
critical_section_occupied = False
client_with_token_idx = 0

def forward_token(requires_critical_section) -> None:
    global client_with_token_idx
    # increment client_with_token_idx to get next client in the ring!
    while not requires_critical_section:
        client_with_token_idx = (client_with_token_idx + 1) % len(clients)

def critical_section_manager(client) -> None:
    """Give access to critical section."""
    global client_with_token_idx
    global critical_section_occupied
    while True:
        if client_with_token_idx == (clients.index(client)-1) % len(clients) and not critical_section_occupied:
            try:
                req = client.recv(1024).decode('utf-8')
                requires_critical_section = True if req == 'true' else False if req == 'done' else False
                # If the current client enters the critical section
                if requires_critical_section:
                    client_with_token_idx, critical_section_occupied = clients.index(client), True
                    print(f'C.S. is occupied by Process-{client_with_token_idx}')
                    requires_critical_section = client.recv(1024).decode('utf-8')
                critical_section_occupied = False
                print(f'C.S. is released by Process-{client_with_token_idx}')
                forward_token(requires_critical_section)
            except:
                print(f'Client {clients.index(client)} disconnected!')
                critical_section_occupied = False
                clients.remove(client)
                forward_token(requires_critical_section)
                break

def recieve_client_connection_req():
    while True:
        client, addr = server.accept()
        print(f"Connected with {str(addr)}")
        clients.append(client)        

        thread = threading.Thread(target=critical_section_manager, args=(client,))
        thread.start()

if __name__ == '__main__':
    print("Server started...")
    server.listen()
    recieve_client_connection_req()