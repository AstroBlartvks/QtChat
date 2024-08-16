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
        try:
            client.sendall(message)
        except:
            continue

def handle(client):
    while True:
        try:
            message = client.recv(1024)
            for cl in CLIENTS:
                if cl != client:
                    cl.sendall(message)
            print(NICKNAMES)
        except:
            index = CLIENTS.index(client)
            nickname = NICKNAMES[index]
            CLIENTS.remove(client)
            client.close()
            broadcast(f"Server: {nickname} покинул сервер!".encode('utf-8'))
            NICKNAMES.remove(nickname)
            break

def receive():
    while True:
        try:
            client, address = server.accept()

            client.sendall('Server: NICK_REQUEST'.encode('utf-8'))
            nickname = client.recv(1024).decode('utf-8')
            NICKNAMES.append(nickname)
            CLIENTS.append(client)

            client.sendall("Подключение к серверу!".encode('utf-8'))
            broadcast(f"Server: {nickname} подключился к серверу!".encode('utf-8'))

            threading.Thread(target=handle, args=(client, )).start()
        except Exception as exp:
            print(f"Error log: {str(exp)}")

receive()
