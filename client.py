from PyQt5 import QtWidgets, QtGui
from form import Ui_MainWindow
import threading
import sys, socket


class mywindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(mywindow, self).__init__()
        self.version = b"2.0.1"
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.server = None
        self.receive_process = None
        self.nickname = ''
        self.my_color = (0, 255, 0, 255)
        self.connection = False
        
        self.ui.pushButton.clicked.connect(self.connect_to)   
        self.ui.pushButton_2.clicked.connect(self.send_msg) 
        self.ui.pushButton_3.clicked.connect(self.disconnect)
        self.ui.pushButton_4.clicked.connect(self.change_color)
    
    def change_color(self):
        color = QtWidgets.QColorDialog.getColor()

        if color.isValid():
            rgba = color.getRgb()
            self.my_color = rgba
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
    
    def get_RGBA64(self, color):
        return QtGui.QRgba64.fromRgba(color[0], color[1], color[2], color[3])

    def create_note(self, message, color, bgcolor=(0, 0, 0, 0)):
        item = QtWidgets.QListWidgetItem(message)
        item.setForeground(QtGui.QColor(color))
        item.setBackground(QtGui.QColor(self.get_RGBA64(bgcolor)))
        self.ui.listWidget.addItem(item)

    def formate(self, text):
        return "\n".join(list([x.rstrip() for x in text.split("\n") if x != "" and x != " " and not(x.count(" ") == len(x))]))

    def disconnect(self):
        if self.connection:
            self.server.close()
            self.create_note("Server: Вы отключились от сервера!", "white", bgcolor=(255, 0, 0, 255))
            self.connection = False
            self.ui.listWidget.scrollToBottom()

    def connect_to(self):
        self.disconnect()
        self.nickname = self.ui.lineEdit_2.text().rstrip()
        if len(self.nickname) > 16:
            self.create_note("Слишком большой ник!", "white", bgcolor=(255, 0, 0, 255))
        elif len(self.nickname) == 0:
            self.create_note("Введите ник!", "white", bgcolor=(255, 0, 0, 255))
        elif "server" in self.nickname.lower():
            self.create_note('"Server" - системное имя.', "white", bgcolor=(255, 0, 0, 255))
        elif sum(list([1 if x in self.nickname else 0 for x in ":\'\"/;"])) > 0:
            self.create_note('Использованы запрещенные символы для ника: :\'\"/;', "white", bgcolor=(255, 0, 0, 255))
        else:
            try:
                self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                HOST, PORT = self.ui.lineEdit.text().split(":")
                self.server.connect((HOST, int(PORT)))
                self.connection = True
                self.receive_process = threading.Thread(target=self.receive)
                self.receive_process.start()
            except:
                self.create_note("Не удалось установить соединение, проверьте IP или сервер", "white", bgcolor=(255, 0, 0, 255))
        self.ui.listWidget.scrollToBottom()

    def send_msg(self):
        raw_text = self.ui.plainTextEdit.toPlainText()
        text = self.formate(raw_text)
        if len(text) == 0:
            self.create_note("Server: Пустое сообщение!", "white", bgcolor=(255, 0, 0, 255))
        else:
            text = f"{self.nickname}: {text}"
            if len(text) > 1024:
                text = text[:1024]
                self.create_note("Ваше сообщение слишком большое и было обрезано!", "white", bgcolor=(255, 0, 0, 255))
            try:
                self.server.sendall(text.encode("utf-8"))
                self.create_note(text, self.get_RGBA64(self.my_color))
            except:
                self.create_note("Вы не подключены к серверу!", "white", bgcolor=(255, 0, 0, 255))
        self.ui.plainTextEdit.setPlainText('')
        self.ui.listWidget.scrollToBottom()

    def receive(self):
        while self.connection:
            try:
                message = self.server.recv(1024).decode("utf-8")
                if message == 'Server: NICK_REQUEST':
                    self.server.sendall(self.version+self.nickname.encode('utf-8'))
                    response = self.server.recv(1024).decode("utf-8")
                    if response != "Подключение к серверу!":
                        self.create_note(response, "white", bgcolor=(255, 0, 0, 255))
                        self.disconnect()
                elif message[:7] == 'Server:':
                    self.create_note(message, "white", bgcolor=(255, 0, 0, 255))
                else:
                    self.create_note(message, self.get_RGBA64((255, 0, 0, 255)))
                self.ui.listWidget.scrollToBottom()
            except:
                break


app = QtWidgets.QApplication([])
application = mywindow()
application.show()
 
sys.exit(app.exec())
