import socket
import threading


class Server:
    def __init__(self, host, port, version):
        self.HOST = host
        self.PORT = port
        self.version = version

        self.CLIENTS = []
        self.NICKNAMES = []
        self.PROCESSES_STATE = []

    def broadcast(self, message, pass_user=None):
        """Пересылка текста всем, за исключением pass_user"""
        for client in self.CLIENTS:
            try:
                if pass_user == client:
                    continue
                client.sendall(message)
            except:
                continue

    def handle(self, client, ID):
        """обработчик клиента на сервере"""
        empty_strings_count = 0
        while self.PROCESSES_STATE[ID]:
            try:
                #Пересылаем сообщения клиента всем, кроме его самого
                message = client.recv(1024)
                if message == b"":
                    empty_strings_count += 1
                    if empty_strings_count > 100:
                        raise Exception("Client doesn't exist!")
                    continue
                if b"<script>" in message or b"</script>" in message:
                    message = message.replace(b"<script>", b"jsstart|")
                    message = message.replace(b"</script>", b"|jsend")
                self.broadcast(message, pass_user=client)
                print(f"LOG: SERVER-NICKNAMES: {self.NICKNAMES} {ID} {self.PROCESSES_STATE[ID]} {client}")
            except Exception as exp:
                #Закрытие клиента
                index = self.CLIENTS.index(client)
                client.close()
                self.broadcast(f"Server: {self.NICKNAMES[index]} покинул сервер!".encode('utf-8'))
                print(f"LOG: ERROR-CLIENT[{self.NICKNAMES[index]}]-TO-SERVER :{str(exp)}")
                #Удаление всех данных, освобождение потока
                self.CLIENTS.remove(client)
                self.NICKNAMES.pop(index)
                self.PROCESSES_STATE[ID] = False
                return
        return


    def check_nickname(self, nickname, version, client, address):
        """Проверка никнейма и версии (играет роль первые 2 цифры, но не третья)"""
        if nickname.replace(" ", "") in self.NICKNAMES or nickname in self.NICKNAMES or version[:3] != self.version[:3]:
            print(f"LOG: DISCONNECT: {address}")
            client.sendall("Никнейм занят или устарелая версия!".encode('utf-8'))
            client.close()
            return False
        else:
            client.sendall("Подключение к серверу!".encode('utf-8'))
            return True


    def run_server(self):
        """Принятие новых клиентов на сервер"""

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.HOST, self.PORT))
        self.server.listen()

        index = 0
        while True:
            try:
                client, address = self.server.accept()
                print(f"LOG: CONNECT: {address}")

                client.sendall('Server: NICK_REQUEST'.encode('utf-8'))
                ver_nick = client.recv(1024).decode('utf-8')
                version = ver_nick[:5]
                nickname = ver_nick[5:]

                #Блок проверки никнейма и пропуск
                is_good_nickname = self.check_nickname(nickname, version, client, address)
                if not is_good_nickname:
                    continue

                self.NICKNAMES.append(nickname)
                self.CLIENTS.append(client)
                self.broadcast(f"Server: {nickname} подключился к серверу!".encode('utf-8'))

                #Создание потока с клиентом
                if False in self.PROCESSES_STATE:
                    #Если есть свободный поток
                    ind = self.PROCESSES_STATE.index(False)
                    self.PROCESSES_STATE[ind] = True
                    process = threading.Thread(target=self.handle, args=(client, ind, ))
                    process.start()
                else:
                    #Если нет свободного потока
                    self.PROCESSES_STATE.append(True)
                    process = threading.Thread(target=self.handle, args=(client, index, ))
                    process.start()
                    index += 1
            except Exception as exp:
                print(f"Error log: {str(exp)}")


server = Server("localhost", 8000, "2.3.0")
server.run_server()

