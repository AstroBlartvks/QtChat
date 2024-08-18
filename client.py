#pip install PyQt5              
#pip install PyQtWebEngine      для QWebEngineView 

from PyQt5 import QtWidgets, QtCore
from form import Ui_MainWindow
import threading
from message_plugin import Messanger
import sys, socket



class MessageWorker(QtCore.QObject):
    htmlChanged = QtCore.pyqtSignal(str)

    def add_message(self, messanger, type_, text, nickname, style):
        threading.Thread(target=self.task, daemon=True, args=(messanger, type_, text, nickname, style,)).start()

    def task(self, messanger, type_, text, nickname, style):
        """Добавляет сообщения в html (подробно об аргументах смотреть в message_pluhin.py)"""
        try:
            res = messanger.change_html(type_, text, nickname, style)
            self.htmlChanged.emit(res)
        except Exception as exp:
            print("CLIENT ERROR (f.add_messgae):", str(exp))


class mywindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(mywindow, self).__init__()
        self.version = b"2.3.0"
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.server = None
        self.receive_process = None
        self.nickname = ''
        self.my_color = "#00ff00"
        self.connection = False
        self.msgWorker = MessageWorker(self)
        self.msgWorker.htmlChanged.connect(self.ui.WebInterface.setHtml)
        
        self.messanger = Messanger()
        self.messanger.load_html()

        self.ui.pushButton.clicked.connect(self.connect_to)   
        self.ui.pushButton_2.clicked.connect(self.send_msg) 
        self.ui.pushButton_3.clicked.connect(self.disconnect)
        self.ui.pushButton_4.clicked.connect(self.change_color)
    
    def change_color(self):
        color = QtWidgets.QColorDialog.getColor()

        if color.isValid():
            rgba = color.getRgb()
            self.my_color = color.name()
            self.ui.frame_3.setStyleSheet("""
            QPushButton{
            background-color: rgb("""+ str(rgba[0]) +"," + str(rgba[1]) + "," + str(rgba[2]) + """);}
            QPushButton:hover{
            background-color: rgb("""+ str(int(rgba[0]*0.8)) +"," + str(int(rgba[1]*0.8)) + "," + str(int(rgba[2]*0.8)) + """);}
            QPushButton:pressed{
            background-color: rgb("""+ str(int(rgba[0]*0.4)) +"," + str(int(rgba[1]*0.4)) + "," + str(int(rgba[2]*0.4)) + """);}
            """)
            
    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question\
        (self, 'Вы нажали на крестик',
            "Вы уверены, что хотите уйти?",
            QtWidgets.QMessageBox.Yes,
            QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.disconnect()
            event.accept()
        else:
            event.ignore()

    def add_message(self, type_, text, nickname=None, style=None):
        """Добавляет сррьщение в html (подробно об аргументах смотреть в message_pluhin.py)"""
        self.msgWorker.add_message(self.messanger, type_, text, nickname, style)

    def formate(self, text):
        return "\n".join(list([x.rstrip() for x in text.split("\n") if x != "" and x != " " and not(x.count(" ") == len(x))]))

    def disconnect(self):
        try:
            if self.connection:
                self.server.close()
                self.add_message("clear", None)
                self.add_message("server", "Вы отключились от сервера!")
                self.connection = False
                self.messanger.clear()
        except Exception as exp:
            print("CLIENT ERROR (f.disconnect):", str(exp))

    def connect_to(self):
        try:
            if self.connection:
                self.add_message("server", "Вы уже на сервере!")
                return
            self.add_message("clear", None)
            
            self.nickname = self.ui.lineEdit_2.text().rstrip()
            if len(self.nickname) > 16:
                self.add_message("client", "Слишком большой ник!")
            elif len(self.nickname) == 0:
                self.add_message("client", "Введите ник!")
            elif "server" in self.nickname.lower():
                self.add_message("client", "\"Server\" - системное имя.")
            elif sum(list([1 if x in self.nickname else 0 for x in ":\'\"/;"])) > 0:
                self.add_message("client", "Использованы запрещенные символы для ника: :\'\"/;")
            else:
                try:
                    self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    HOST, PORT = self.ui.lineEdit.text().split(":")
                    self.server.connect((HOST, int(PORT)))
                    self.connection = True
                    self.receive_process = threading.Thread(target=self.receive)
                    self.receive_process.start()
                except Exception as exp:
                    print("CLIENT ERROR (f.connect_to.2):", str(exp))
                    self.add_message("server", "Не удалось установить соединение, проверьте IP или сервер")
        except Exception as exp:
            print("CLIENT ERROR (f.connect_to.1):", str(exp))

    def send_msg(self):
        try:
            raw_text = self.ui.plainTextEdit.toPlainText()
            if "<!-- START BODY -->" in raw_text or "<!-- END BODY -->" in raw_text:
                self.add_message("client", "Запрещено использовать такие сообщения!")
                return
            
            text = self.formate(raw_text)
            if len(text) == 0:
                self.add_message("client", "Пустое сообщение!")
                return
            
            to_server_text = f"{self.nickname}: {text}"
            if len(to_server_text) > 1024:
                to_server_text = to_server_text[:1024]
                self.add_message("client", "Ваше сообщение слишком большое и было обрезано!")
            try:
                self.server.sendall(to_server_text.encode("utf-8"))
                self.add_message("myself", text[:1024 - len(self.nickname)], self.nickname, style=f"color:{self.my_color}")
            except:
                self.add_message("client", "Вы не подключены к серверу!")

            self.ui.plainTextEdit.setPlainText('')
        except Exception as exp:
                print("CLIENT ERROR (f.send_msg):", str(exp))

    def receive(self):
        try:
            empty_strings_count = 0

            while self.connection:
                try:
                    message = self.server.recv(1024)
                    message = message.decode("utf-8")

                    if message == "":
                        empty_strings_count += 1
                        if empty_strings_count > 100:
                            self.disconnect()
                            self.add_message("client", "Произошла ошибка на сервере! Скорее всего он выключился!")
                            return 
                        continue

                    if message == 'Server: NICK_REQUEST':
                        self.server.sendall(self.version+self.nickname.encode('utf-8'))
                        response = self.server.recv(1024).decode("utf-8")
                        
                        if not("Подключение к серверу!" in response):
                            self.add_message("server", response)
                            self.disconnect()
                        if "Подключение к серверу!" in response and "Server:" in response:
                            #Фикс бага с склейкой "Подключение к серверу!" и "Server" {user_name} подключился к серверу!"
                            response = response.split("!")[0] + "!\n" + response.split("!")[1] + "!"
                            self.add_message("server", response)

                    elif message[:7] == 'Server:':
                        self.add_message("server", message)
                    else:
                        nick = message.split(":")[0]
                        msg = message.split(":")[1]
                        self.add_message("friend", msg, nick)
                    #self.ui.listWidget.scrollToBottom()
                except Exception as exp:
                    print("CLIENT ERROR (f.recieve.2):", str(exp))
        except Exception as exp:
            print("CLIENT ERROR (f.recieve.1):", str(exp))


app = QtWidgets.QApplication([])
application = mywindow()
application.show()
 
sys.exit(app.exec())
