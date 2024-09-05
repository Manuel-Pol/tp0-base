from common.bet_header import BetHeader
from common.bet_package import BetPackage
from common.utils import Bet
from common.safe_sockets import safe_read
from enum import Enum
import logging

CLIENT_ID_SIZE = 1
MSG_TYPE_SIZE = 1

class MsgType(Enum):
    SUCCESS = 0
    FAIL = 1
    BETS = 2
    NO_MORE_BETS = 3
    CONSULT_WINNER = 4
    WINNERS = 5

def recv_message(socket):
    msg_type_data = safe_read(socket, MSG_TYPE_SIZE)
    msg_type = int.from_bytes(msg_type_data, 'big')
    return process_msg(msg_type, socket)

def process_msg(type, socket):
    try:
        type = MsgType(type)
    except ValueError:
        print("No existe ningún tipo para ese valor")
        return
    if type == MsgType.SUCCESS:
        return (None, None)
    if type == MsgType.FAIL:
        return (None, None)
    if type == MsgType.BETS:
        return recv_bets(socket)
    if type == MsgType.NO_MORE_BETS:
        return (MsgType.NO_MORE_BETS, recv_client_id(socket))
    if type == MsgType.CONSULT_WINNER:
        return (MsgType.CONSULT_WINNER, recv_client_id(socket))
    if type == MsgType.WINNERS:
        return (None, None)
    
def recv_bets(socket):
    bet_header = BetHeader.deserialize(socket)
    # logging.debug(f'BET_HEADER {bet_header}')
    bets = []
    for _ in range(int(bet_header.amount_bets)):
        bet_package = BetPackage.deserialize(socket)
        # logging.debug(f'BET {bet_package}')
        bet = Bet(bet_header.agency, bet_package.name, bet_package.lastname, bet_package.document, bet_package.birthday, bet_package.number)
        bets.append(bet)
    
    return (MsgType(MsgType.BETS), (bet_header, bets))

def recv_client_id(socket):
    bclient_id_size = int.from_bytes(safe_read(socket, CLIENT_ID_SIZE), 'big')
    cliend_id = safe_read(socket, bclient_id_size).decode()
    return cliend_id

def send_winners(socket, amount_winners):
    msg_bytes = MsgType.WINNERS.value.to_bytes(1, 'big') + amount_winners.to_bytes(1, 'big')
    socket.sendall(msg_bytes)
    