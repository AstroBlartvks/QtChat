#pip install PyQt5              
#pip install PyQtWebEngine      для QWebEngineView 

import sys
import socket
import threading

from form import Ui_MainWindow
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets

import add.add_utils as utils

from add.new_socket import New_socket
from message_plugin import Messanger


class MessageWorker(QtCore.QObject):
    """ОТОБРАЖЕНИЕ HTML СТРАНИЧКИ ДЛЯ СООБЩЕНИЙ"""
    htmlChanged = QtCore.pyqtSignal(str)

    def add_message(self, messanger, type_, text, nickname, style):
        """Типо создать процесс, который поменяет html, хз как оно работает, по другому никак"""
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
        """КЛАСС ОКНА"""
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QtGui.QIcon("./icons/icon.png"))

        self.creeate_class_variable()
        self.create_additions()
        self.connect_buttons()

    def creeate_class_variable(self):
        """СОЗДАВАТЬ ПЕРЕМЕННЫЕ КЛАССА"""
        #bool
        self.connection = False

        #strings
        self.version  = b"2.3.1"
        self.my_color = "#00ff00"
        self.nickname = ''

        #other
        self.server = None
        self.receive_process = None


    def create_additions(self):
        """СОЗДАВАТЬ ДОПОЛНИТЕЛЬНЫЕ КЛАССЫ"""
        self.msgWorker = MessageWorker(self)
        self.msgWorker.htmlChanged.connect(self.ui.WebInterface.setHtml)

        self.new_socket = New_socket(path_dll="./add/new_socket.dll")

        self.messanger = Messanger()
        self.messanger.load_html()

    def connect_buttons(self):
        """ПРИКРЕПИТЬ КНОПКИ"""
        self.ui.pushButton_5.setIcon(QtGui.QIcon("icons/attach.png"))
        self.ui.pushButton_5.setIconSize(QtCore.QSize(32, 32))
        self.ui.pushButton.clicked.connect(self.connect_to)   
        self.ui.pushButton_2.clicked.connect(self.send_msg) 
        self.ui.pushButton_3.clicked.connect(self.disconnect)
        self.ui.pushButton_4.clicked.connect(self.change_color)
        self.ui.pushButton_5.clicked.connect(self.add_file)
    
    def add_file(self):
        """Добавление файлов"""
        try:
            print("No")
        except Exception as exp:
            print(exp)

    def change_color(self):
        """СМЕНА ЦВЕТА ТЕКСТУ"""
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
        """ЗАКРЫТИЕ ОКНА"""
        result = self.new_socket.msg_value("Вы нажали на крестик", "Вы уверены, что хотите уйти?")
        if result == 6:
            self.disconnect()
            event.accept()
        else:
            event.ignore()

    def add_message(self, type_, text, nickname=None, style=None):
        """Добавляет сообщения в html (подробно об аргументах смотреть в message_plugin.py)"""
        self.msgWorker.add_message(self.messanger, type_, text, nickname, style)

    def disconnect(self):
        """Попытка выхода"""
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
        """Попытка присоединиться"""
        try:
            if self.connection:
                return self.add_message("server", "Вы уже на сервере!")
            self.add_message("clear", None)
            
            self.nickname = self.ui.lineEdit_2.text().rstrip()
            if len(self.nickname) > 16:
                return self.add_message("client", "Слишком большой ник!")
            elif len(self.nickname) == 0:
                return self.add_message("client", "Введите ник!")
            elif "server" in self.nickname.lower():
                return self.add_message("client", "\"Server\" - системное имя.")
            elif sum(list([1 if x in self.nickname else 0 for x in ":\'\"/;"])) > 0:
                return self.add_message("client", "Использованы запрещенные символы для ника: :\'\"/;")

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
        """Отпрвка сообщений"""
        try:
            raw_text = self.ui.plainTextEdit.toPlainText()
            if "<!-- START BODY -->" in raw_text or "<!-- END BODY -->" in raw_text:
                self.add_message("client", "Запрещено использовать такие сообщения!")
                return
            
            text = utils.formate_text(raw_text)
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
        """Попытка получения сообщений"""
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
                        msg = ":".join(message.split(":")[1:])
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
