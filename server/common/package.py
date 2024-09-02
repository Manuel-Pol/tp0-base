import socket
import logging
import signal
import sys
import logging

MAX_STR_SIZE_BYTES = 1
MAX_IDENTITY_SIZE_BYTES = 4
MAX_NUMBER_SIZE_BYTES = 2

class Package:

#                                                                    chequear esto
    def __init__(self, name: str, lastname: str, identity_card: int, birthday: str, number: int):
        self.name = name
        self.lastname = lastname
        self.identity_card = identity_card
        self.birthday = birthday
        self.number = number

    def serialize(self) -> bytes:
        bname = self.name.encode()
        bname_size = len(bname).to_bytes(MAX_STR_SIZE_BYTES, 'big')

        blastname = self.lastname.encode()
        blastname_size = len(blastname).to_bytes(MAX_STR_SIZE_BYTES, 'big')
        
        bbirthday = self.birthday.encode()
        bbirthday_size = len(bbirthday).to_bytes(MAX_STR_SIZE_BYTES, 'big')
        
        bidentity_card = self.identity_card.to_bytes(MAX_IDENTITY_SIZE_BYTES, 'big')
        
        bnumber = self.number.to_bytes(MAX_NUMBER_SIZE_BYTES, 'big')
        return bname_size + bname + blastname_size + blastname + bidentity_card + bbirthday_size + bbirthday + bnumber

    def deserialize(data: bytes) -> 'Package':
        pass