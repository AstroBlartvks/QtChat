from PyQt5 import QtWidgets, QtGui
from form import Ui_MainWindow
import threading
import sys, socket


class mywindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.server = None
        self.receive_process = None
        self.nickname = ''
        self.connection = False
        
        self.ui.pushButton.clicked.connect(self.connect_to)   
        self.ui.pushButton_2.clicked.connect(self.send_msg) 
    
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
    
    def create_note(self, message, color):
        item = QtWidgets.QListWidgetItem(message)
        item.setForeground(QtGui.QColor(color))
        self.ui.listWidget.addItem(item)

    def formate(self, text):
        return "\n".join(list([x.rstrip() for x in text.split("\n") if x != "" and x != " " and not(x.count(" ") == len(x))]))

    def disconnect(self):
        if self.connection:
            self.server.close()
            self.create_note("Server: Вы отключились от сервера!", "purple")
            self.connection = False
            self.ui.listWidget.scrollToBottom()

    def connect_to(self):
        self.disconnect()
        self.nickname = self.ui.lineEdit_2.text().rstrip()
        if len(self.nickname) > 16:
            self.create_note("Слишком большой ник!", "purple")
        elif len(self.nickname) == 0:
            self.create_note("Введите ник!", "purple")
        elif self.nickname.replace(" ", "") == 'Server':
            self.create_note('"Server" - системное имя.', "purple")
        elif self.nickname.find(':') != -1:
            self.create_note('":" - запрещённый символ для ника.', "purple")
        else:
            try:
                self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                HOST, PORT = self.ui.lineEdit.text().split(":")
                self.server.connect((HOST, int(PORT)))

                self.connection = True

                self.receive_process = threading.Thread(target=self.receive).start()
            except:
                self.create_note("Слишком большой ник!", "purple")
        self.ui.listWidget.scrollToBottom()

    def send_msg(self):
        raw_text = self.ui.plainTextEdit.toPlainText()
        text = self.formate(raw_text)
        if len(text) == 0:
            self.create_note("Server: Пустое сообщение!", "purple")
        else:
            text = f"{self.nickname}: {text}"
            if len(text) > 1024:
                text = text[:1024]
                self.create_note("Ваше сообщение слишком большое и было обрезано!", "purple")
            try:
                self.server.sendall(text.encode("utf-8"))
                self.create_note(text, "green")
            except:
                self.create_note("Вы не подключены к серверу!", "purple")
        self.ui.plainTextEdit.setPlainText('')
        self.ui.listWidget.scrollToBottom()


    def receive(self):
        while self.connection:
            try:
                message = self.server.recv(1024).decode("utf-8")
                if message == 'Server: NICK_REQUEST':
                    self.server.sendall(self.nickname.encode('utf-8'))
                elif message[:7] == 'Server:':
                    self.create_note(message, "purple")
                else:
                    self.create_note(message, "red")
                self.ui.listWidget.scrollToBottom()
            except:
                break



app = QtWidgets.QApplication([])
application = mywindow()
application.show()
 
sys.exit(app.exec())
