import socket, time
import threading

HOST = "localhost"
PORT = 8000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

CLIENTS = []
NICKNAMES = []

def broadcast(message):
    for client in CLIENTS:
        client.sendall(message)

def handle(client):
    while True:
        try:
            message = client.recv(1024)
            for cl in CLIENTS:
                if cl != client:
                    cl.sendall(message)
        except:
            index = CLIENTS.index(client)
            nickname = NICKNAMES[index]
            CLIENTS.remove(client)
            client.close()
            broadcast(f"{nickname} left!".encode('utf-8'))
            NICKNAMES.remove(nickname)
            break

def receive():
    global NICKNAMES
    while True:
        client, address = server.accept()

        client.sendall('NICK_REQUEST'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        NICKNAMES.append(nickname)
        CLIENTS.append(client)

        client.sendall("Connected to server!".encode('utf-8'))
        broadcast(f"{nickname} joined!".encode('utf-8'))

        threading.Thread(target=handle, args=(client,)).start()


receive()
