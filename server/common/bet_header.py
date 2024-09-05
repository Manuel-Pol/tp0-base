from common.bet_package import MAX_STR_SIZE_BYTES
from common.safe_sockets import safe_read


class BetHeader:

    def __init__(self, agency: str, amount_bets: str):
        self.agency = agency
        self.amount_bets = amount_bets

    def serialize(self) -> bytes:
        bagency = self.agency.encode()
        bagency_size = len(bagency).to_bytes(MAX_STR_SIZE_BYTES, 'big')

        bamount_bets = self.amount_bets.encode()
        bamount_bets_size = len(bamount_bets).to_bytes(MAX_STR_SIZE_BYTES, 'big')

        return bagency_size + bagency + bamount_bets_size + bamount_bets
    
    def deserialize(socket) -> 'BetHeader':
        bagency_size = int.from_bytes(safe_read(socket, MAX_STR_SIZE_BYTES), 'big')
        agency = safe_read(socket, bagency_size).decode()

        bamount_bets_size = int.from_bytes(safe_read(socket, MAX_STR_SIZE_BYTES), 'big')
        amount_bets = safe_read(socket, bamount_bets_size).decode()

        return BetHeader(agency, amount_bets)

    def __getattribute__(self, name):
        return super().__getattribute__(name)
    
    def __str__(self) -> str:
        return f"Agency {self.agency} sent {self.amount_bets} bets"