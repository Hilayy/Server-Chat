import sys
from socket import *
import time
import random
import requests
import threading


def get_open_port():
    s = socket(AF_INET, SOCK_STREAM)
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def save_socket_details():
    with open('/Users/User/Desktop/socket details.txt', 'w+') as f:
        f.writelines(str(HOST) + "\n")
        f.write(str(PORT) + "\n")
        f.write(PASSWORD)


def quit_mode(client_socket):
    client_socket.send('Enter the password to end the connection.'.encode('utf-8'))
    while True:
        data = client_socket.recv(BUFSIZ)
        if data.decode('utf-8') == PASSWORD:
            client_socket.send('Password is correct, ending connection.'.encode('utf-8'))
            return True
        else:
            client_socket.send('Password is incorrect, returning to session.'.encode('utf-8'))
            return False


def get_up_time():
    now_time = time.time()
    diff_time = round((now_time - start_time), 2)
    return "The server is up for {} seconds".format(diff_time).encode('utf-8')


def get_msg_count(msg_count):
    return ('You sent {} messages'.format(msg_count)).encode('utf-8')


def get_joke():
    response = requests.get("https://official-joke-api.appspot.com/random_joke")
    if response.status_code == 200:
        joke = response.json()
        data = joke['setup'] + joke['punchline']
    else:
        return "Couldn't retrieve a joke."
    return str(data).encode('utf-8')


def shuffle_data(data):
    words = data.split()
    shuffled_words = []
    for word in words:
        shuffled_word = ''.join(random.sample(word, len(word)))
        shuffled_words.append(shuffled_word)
    return (' '.join(shuffled_words)).encode('utf-8')


def get_shuffle_status():
    global is_shuffle
    is_shuffle = not is_shuffle
    status = "on" if is_shuffle else "off"
    return ("Shuffle mode is now {}".format(status)).encode('utf-8')


def handle_client(client_socket, client_address):
    global client_sockets
    print(f"Connection by {client_address}")
    client_sockets.append(client_socket)
    threading.Thread(target=msg_from_client, args=(client_socket, client_address)).start()


def msg_from_client(client_socket, client_address):
    global disconnected_clients
    msg_count = 0
    while True:
        try:
            data = client_socket.recv(BUFSIZ)
            if not data:
                break
            msg_count += 1
            print(f"{client_address}: {data.decode('utf-8')}")
            quit_sequence = send_to_client(client_socket, data.decode('utf-8'), msg_count)
            if quit_sequence:
                print(quit_sequence)
                disconnected_clients += 1
                break
        except Exception as e:
            print(f"Error reading message from {client_socket}: {e}")
            break
    client_socket.close()


def send_to_client(client_sock, msg, msg_count):
    if msg == 'quit':
        end = quit_mode(client_sock)
        if end:
            print(f'end: {end}')
            return True
        return False
    elif msg == 'TIME':
        msg = get_up_time()
    elif msg == 'COUNT':
        msg = get_msg_count(msg_count)
    elif msg == 'JOKE':
        msg = get_joke()
    elif msg == 'SHUFFLE':
        msg = get_shuffle_status()
    elif is_shuffle:
        msg = shuffle_data(msg)
    else:
        msg = msg.encode('utf-8')
    client_sock.send(msg)


PASSWORD = 'password'
HOST = 'localhost'
PORT = get_open_port()
save_socket_details()

BUFSIZ = 1024
ADDR = (HOST, PORT)

server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(ADDR)
server_socket.listen(2)
start_time = time.time()
is_shuffle = False
client_sockets = []
disconnected_clients = 0


def accept_client():
    while disconnected_clients == 0:
        try:
            client_socket, client_address = server_socket.accept()
            threading.Thread(target=handle_client, args=(client_socket, client_address)).start()
        except Exception as e:
            print(f"Error:{e}")
            break


threading.Thread(target=accept_client).start()

while disconnected_clients == 0:
    time.sleep(0.3)

for socket in client_sockets:
    socket.close()
server_socket.close()
sys.exit(0)

