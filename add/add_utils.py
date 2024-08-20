from PyQt5 import QtCore
import threading


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


def formate_text(text):
    return "\n".join(list([x.rstrip() for x in text.split("\n") if x != "" and x != " " and not(x.count(" ") == len(x))]))


def check_nicknames(nickname, add_message):
    if len(nickname) > 16:
        add_message("client", "Слишком большой ник!")
        return "BAD_NICKNAME"
    elif len(nickname) == 0:
        add_message("client", "Введите ник!")
        return "BAD_NICKNAME"
    elif "server" in nickname.lower():
        add_message("client", "\"Server\" - системное имя.")
        return "BAD_NICKNAME"
    elif sum(list([1 if x in nickname else 0 for x in ":\'\"/;"])) > 0:
        add_message("client", "Использованы запрещенные символы для ника: :\'\"/;")
        return "BAD_NICKNAME"
    return "GOOD_NICKNAME"
