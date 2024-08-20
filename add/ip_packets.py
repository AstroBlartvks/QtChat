import hashlib

class Utils:
    """
    Утилиты дял работы с данными пакета:\n
    1. ХЭШ: create_hash, load_hash
    2. РАЗМЕР: save_size, load_size
    """
    def create_hash(text: bytes) -> bytes:
        """Создает хэш:\n
            input: данные чего-либо bytes (закодированный ex: utf-8)\n
            return: готовые bytes к пакету
        """
        value = hashlib.sha256(text).hexdigest()
        return "".join(list([chr(int(value[x:x+2], 16)) for x in range(0, len(value), 2)])).encode("utf-8")

    def load_hash(text: bytes) -> str:
        """Преобразует хэш из пакета:\n
            input: bytes, хэш внутри пакета\n
            return: str, выводит хэш hex\n
        """
        text = text.decode("utf-8")
        return "".join(list(["0" + hex(ord(x))[2:] if len(hex(ord(x))[2:]) == 1 else hex(ord(x))[2:] for x in text]))

    def save_size(length: int) -> bytes:
        """Преобразует длину данных в bytes из int"""
        length = hex(length)[2:]
        value = "0" * (16 - len(length)) + length
        return "".join(list([chr(int(value[x:x+2], 16)) for x in range(0, len(value), 2)])).encode("utf-8")

    def load_size(length: bytes) -> int:
        """Преобразует длину данных из bytes в int"""
        length = "".join(list([str(hex(ord(x))[2:]) for x in length.decode("utf-8")]))
        length = "0" * (16 - len(length)) + length
        return int(length, 16)


class Packet:
    def __init__(self, packet_size: int = 1024):
        """
            Класс, который реализует пакеты\n
            потом использовать self.compose(data), который выдаст пакет -> bytes\n
            self.version:   b-str   CONST         4b  \n         
            self.hash:      b-str   CHANGEABLE    48b \n
            self.size:      b-str   CHANGEABLE    8b  \n
            self.data:      b-str   CHANGEABLE    Nb  \n
            ==================================  Nb + 60b
        """
        self.version = b"0003"
        self.hash_value = b""
        self.size = b""
        self.packet_size = packet_size

    def __is_valid_data(self, data):
        """Проверка данных на валидность, не трогать!"""
        if data is None: 
            return b""
        elif isinstance(data, bytes):
            return data
        raise Exception(f"\n\nДанные, которые поступают в пакет должны быть типа {type(b"ASTRO-TOP, RA1W-TOP")}, а не {type(data)}\n")

    def __hashing(self) -> None:
        """Не использовать, лучше prepare"""
        self.hash_value = Utils.create_hash(self.data)
    
    def __sizing(self) -> None:
        """Не использовать, лучше prepare"""
        self.size = Utils.save_size(len(self.data))

    def prepare(self) -> None:
        """Создает хэш data и вычисляет размер пакета"""
        self.__hashing()
        self.__sizing()
    
    def compose(self, data: bytes) -> bytes:
        """Компонует всё в пакет\nВОЗВРАЩАЕТ БАЙТЫ ДЛЯ ОТПРАВКИ"""
        self.data = self.__is_valid_data(data)
        self.prepare()
        return self.version + self.hash_value + self.size + self.data

    def decompose(self, packet: bytes):
        """Декомпилировать пакет\nВОЗВРАЩАЕТ КЛАСС ПАКЕТА С ДАННЫМИ И ХЭШЕМ"""
        try:
            version = packet[0:4]
            if version != self.version:                          
                raise Exception(f"Версия пакетов не совпадает: our-{self.version} other-{version}")
            
            hash_packet = packet[4:53]
            size_packet = packet[53:61]
            data = packet[61:]
            completed = self.check_packet(hash_packet, size_packet, data)
            if not completed:
                print(f"Пакет испорчен, но сохранён")
                print(self.__str__())
                return False
            
            ipp_packet = Packet()
            ipp_packet.compose(data)
            return ipp_packet
        except Exception as exp:
            print(f"ERROR: {str(exp)}")
            return False

    def text(self, encoding = "utf-8"):
        return self.data.decode(encoding=encoding)

    def check_packet(self, hash_value: bytes, size: bytes, data: bytes) -> bool:
        """Проверяет правильность пакета"""
        self.data = data
        self.prepare()
        if (self.hash_value != hash_value) or (self.size != size):
            return False
        return True

    def __str__(self):
        """Вывод данных о пакете"""
        return f"\nVERSION: {self.version}\nДанные:        {self.data}\nХэш:           {Utils.load_hash(self.hash_value)}\nПакет-хэш:     {self.hash_value}\b\nРазмер:        {Utils.load_size(self.size)}\nПакет-Размер:  {self.size}\n"
