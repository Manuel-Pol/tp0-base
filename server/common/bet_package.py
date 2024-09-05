from common.safe_sockets import safe_read

MAX_STR_SIZE_BYTES = 1

class BetPackage:

    def __init__(self, name: str, lastname: str, document: str, birthday: str, number: str):
        self.name = name
        self.lastname = lastname
        self.document = document
        self.birthday = birthday
        self.number = number

    def serialize(self) -> bytes:
        bname = self.name.encode()
        bname_size = len(bname).to_bytes(MAX_STR_SIZE_BYTES, 'big')
        
        blastname = self.lastname.encode()
        blastname_size = len(blastname).to_bytes(MAX_STR_SIZE_BYTES, 'big')

        bbirthday = self.birthday.encode()
        bbirthday_size = len(bbirthday).to_bytes(MAX_STR_SIZE_BYTES, 'big')
        
        bdocument = self.document.encode()
        bdocument_size = len(bdocument).to_bytes(MAX_STR_SIZE_BYTES, 'big')

        bnumber = self.number.encode()
        bnumber_size = len(bnumber).to_bytes(MAX_STR_SIZE_BYTES, 'big')

        return bname_size + bname + blastname_size + blastname + bdocument_size + bdocument + bbirthday_size + bbirthday + bnumber_size + bnumber
    
    def deserialize(socket) -> 'BetPackage':
        bname_size = int.from_bytes(safe_read(socket, MAX_STR_SIZE_BYTES), 'big')
        name = safe_read(socket, bname_size).decode()

        blastname_size = int.from_bytes(safe_read(socket, MAX_STR_SIZE_BYTES), 'big')
        lastname = safe_read(socket, blastname_size).decode()

        bdocument_size = int.from_bytes(safe_read(socket, MAX_STR_SIZE_BYTES), 'big')
        document = safe_read(socket, bdocument_size).decode()

        bbirthday_size = int.from_bytes(safe_read(socket, MAX_STR_SIZE_BYTES), 'big')
        birthday = safe_read(socket, bbirthday_size).decode()

        bnumber_size = int.from_bytes(safe_read(socket, MAX_STR_SIZE_BYTES), 'big')
        number = safe_read(socket, bnumber_size).decode()

        return BetPackage(name, lastname, document, birthday, number)

    def __getattribute__(self, name):
            return super().__getattribute__(name)
    
    def __str__(self) -> str:
        return f"Bet from {self.name} {self.lastname}, {self.birthday}, DNI {self.document}; of value {self.number}"