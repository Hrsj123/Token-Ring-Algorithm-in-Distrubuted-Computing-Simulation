import socket
import threading
import random
import time

# Client configuration
SERVER = "127.0.0.1"
PORT = 12345
ADDR = (SERVER, PORT)

# Create the client socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def dummy_process_resource_requirement():
    """Mimics a process
        0 -> process does not require critical section
        `other num's` -> Time in secs for which critical section will be occupied
    """
    # Weights: Higher weight for 0, equal weights for 2, 3, 4, and 5
    weights = [3, 1, 1]

    # Sample from the weighted distribution
    choices = [0, 2, 3]
    number = random.choices(choices, weights=weights)[0]
    return number

def execute_process(*args):
    print('Executing the process...')
    time.sleep(args[0])                        # This mimics the process currently occupying C.S.
    print('Process execution finished!')

def critical_section_request():
    while True:
        req_time = dummy_process_resource_requirement()
        if req_time:
            try:
                access = client.send(f'true'.encode('utf-8')) # request for C.S.
                if access:
                    execute_process(req_time)
                    client.send('done'.encode('utf-8'))
            except:
                print("An error occurred!")
                client.close()
                break
        else:
            # The client will stop asking for C.S. for 2 secs!
            time.sleep(2)               


if __name__ == '__main__':
    print("Client started...")
    write_thread = threading.Thread(target=critical_section_request)
    write_thread.start()