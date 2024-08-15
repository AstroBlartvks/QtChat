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
        
        self.ui.pushButton.clicked.connect(self.connect_to)   
        self.ui.pushButton_2.clicked.connect(self.send_msg) 

    def connect_to(self):

        self.nickname = self.ui.lineEdit_2.text()
        print(self.nickname)
        if len(self.nickname) > 16:
            item = QtWidgets.QListWidgetItem("Server: Слишком большой ник")
            item.setForeground(QtGui.QColor("purple"))
            self.ui.listWidget.addItem(item)
            self.server.close()
        elif len(self.nickname) == 0:
            item = QtWidgets.QListWidgetItem("Server: Введите ник")
            item.setForeground(QtGui.QColor("purple"))
            self.ui.listWidget.addItem(item)
            self.server.close()
        else:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            HOST, PORT = self.ui.lineEdit.text().split(":")
            self.server.connect((HOST, int(PORT)))

            self.receive_process = threading.Thread(target=self.receive).start()

    def send_msg(self):
        text = f"{self.nickname}: {self.ui.plainTextEdit.toPlainText()}"
        item = QtWidgets.QListWidgetItem(text)
        item.setForeground(QtGui.QColor("green"))
        self.ui.listWidget.addItem(item)
        try:
            self.server.sendall(text.encode("utf-8"))
        except:
            item = QtWidgets.QListWidgetItem("Server: Вы не подключены к серверу")
            item.setForeground(QtGui.QColor("purple"))
            self.ui.listWidget.addItem(item)


    def receive(self):
        while True:
            try:
                message = self.server.recv(1024).decode("utf-8")
                if message == 'NICK_REQUEST':
                    self.server.sendall(self.nickname.encode('utf-8'))
                else:
                    item = QtWidgets.QListWidgetItem(message)
                    item.setForeground(QtGui.QColor("red"))
                    self.ui.listWidget.addItem(item)

            except:
                print("TY LOH")
                self.server.close()
                break



app = QtWidgets.QApplication([])
application = mywindow()
application.show()
 
sys.exit(app.exec())
