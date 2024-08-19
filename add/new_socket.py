import ctypes


class New_socket:
    def __init__(self, path_dll=None):
        """TEST USING C++ DLLS"""
        try:
            self.dll = ctypes.CDLL(path_dll)
        except Exception as exp:
            print(f"{str(exp)}\nОШИБКА, СКОРЕЕ ВСЕГО НЕ ВЕРЕН ПУТЬ ДО DLL, НО ЭТО НЕ ТОЧНО!!!")
        self.responses = {6: "YES", 7:"NO"}
        self.encoding = "CP1251"
    
    def char_encode(self, text: str) -> bytes:
        return ctypes.c_char_p(text.encode(self.encoding))

    def msg_value(self, title: str, message: str) -> int:
        """title - заголовок msgbox\nmessage - текст в msgbox\nВыводит результат, где 6 - YES, 7 - NO"""
        return self.dll.msg_value(self.char_encode(message), self.char_encode(title))
    
    def define_result(self, value: int) -> str:
        return self.responses[value]
        


