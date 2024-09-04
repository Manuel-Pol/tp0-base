MAX_STR_SIZE_BYTES = 1
MAX_IDENTITY_SIZE_BYTES = 4
MAX_NUMBER_SIZE_BYTES = 2

class Package:

    def __init__(self, name: str, lastname: str, document: int, birthday: str, number: int):
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
        
        bdocument = self.document.to_bytes(MAX_IDENTITY_SIZE_BYTES, 'big')

        bnumber = self.number.to_bytes(MAX_NUMBER_SIZE_BYTES, 'big')

        return bname_size + bname + blastname_size + blastname + bdocument + bbirthday_size + bbirthday + bnumber
    
    def deserialize(data: bytes) -> 'Package':
        init, finish = 0, MAX_STR_SIZE_BYTES
        bname_size = int.from_bytes(data[init:finish], 'big')
        
        init, finish = finish, finish + bname_size
        name = data[init:finish].decode()

        init, finish = finish, finish + MAX_STR_SIZE_BYTES
        blastname_size = int.from_bytes(data[init:finish], 'big')
        
        init, finish = finish, finish + blastname_size
        lastname = data[init:finish].decode()
        
        init, finish = finish, finish + MAX_IDENTITY_SIZE_BYTES
        document = int.from_bytes(data[init:finish], 'big')

        init, finish = finish, finish + MAX_STR_SIZE_BYTES
        bbirthday_size = int.from_bytes(data[init:finish], 'big')
        
        init, finish = finish, finish + bbirthday_size
        birthday = data[init:finish].decode()

        init, finish = finish, finish + MAX_NUMBER_SIZE_BYTES
        number = int.from_bytes(data[init:finish], 'big')

        return Package(name, lastname, document, birthday, number)

    def __getattribute__(self, name):
            return super().__getattribute__(name)
    
    def __str__(self) -> str:
        return f"Bet from {self.name} {self.lastname}, {self.birthday}, DNI {self.document}; of value {self.number}"