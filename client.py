from PyQt5 import QtWidgets, QtGui
from form import Ui_MainWindow  # импорт нашего сгенерированного файла
import threading
import sys, socket


class mywindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.server = None
        self.process = None
        
        self.ui.pushButton.clicked.connect(self.connect_to)   
        self.ui.pushButton_2.clicked.connect(self.send_msg) 

    def connect_to(self):
        self.exist = False
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        HOST, PORT = self.ui.lineEdit.text().split(":")
        self.server.connect((HOST, int(PORT)))
        self.process = threading.Thread(target=self.get_packets)
        self.exist = True
        self.process.start()

    def send_msg(self):
        text = self.ui.plainTextEdit.toPlainText()
        nickname = self.ui.lineEdit_2.text()
        nickname = (nickname + 16 * " ")[:16]
        text = nickname + text
        item = QtWidgets.QListWidgetItem(f"{nickname.replace(' ', '')}: {text[16:]}")
        item.setForeground(QtGui.QColor("green"))
        self.ui.listWidget.addItem(item)
        self.server.sendall(text.encode("utf-8"))


    def get_packets(self):
        while self.exist:
            packet = self.server.recv(1024).decode("utf-8")
            text = packet[16:]
            text = " =>\n => ".join(list([text[x:x+50] for x in range(0, len(text), 50)]))
            item = QtWidgets.QListWidgetItem(f"{packet[:16].replace(' ', '')}: {text}")
            item.setForeground(QtGui.QColor("red"))
            self.ui.listWidget.addItem(item)



app = QtWidgets.QApplication([])
application = mywindow()
application.show()
 
sys.exit(app.exec())
#fskdfs
