import socket
import logging
import signal
import sys
import logging
from common.utils import Bet, store_bets
from common.bet_package import BetPackage
from common.bet_header import BetHeader

def recv_bets(socket):
    bet_header = BetHeader.deserialize(socket)
    logging.debug(f'BET_HEADER {bet_header}')
    bets = []
    for _ in range(int(bet_header.amount_bets)):
        bet_package = BetPackage.deserialize(socket)
        logging.debug(f'BET {bet_package}')
        bet = Bet(bet_header.agency, bet_package.name, bet_package.lastname, bet_package.document, bet_package.birthday, bet_package.number)
        bets.append(bet)
    
    return bet_header, bets


def send_confirmation(socket):
    num = 0
    data = num.to_bytes(1, 'big')
    socket.sendall(data)

class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)

    def _handle_sigterm(self, sig, frame):
        """
        Handle SIGTERM signal so the server close gracefully.
        """
        logging.info("action: handle_signal | signal: SIGTERM | result: in_progress")
        self._server_socket.close()
        logging.info("action: handle_signal | signal: SIGTERM | result: success")

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        # TODO: Modify this program to handle signal to graceful shutdown
        # the server

        signal.signal(signal.SIGTERM, self._handle_sigterm)

        while True:
            try:
                client_sock = self.__accept_new_connection()
                self.__handle_client_connection(client_sock)
            except OSError as error:
                break

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            # TODO: Modify the receive to avoid short-reads
            addr = client_sock.getpeername()
            logging.info(f'action: receive_message | result: in_progress')
            bet_header, bets = recv_bets(client_sock)
            logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {bet_header}')
            store_bets(bets)
            for bet in bets:
                logging.info(f'action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}')
            # msg = client_sock.recv(1024).rstrip().decode('utf-8')
            # TODO: Modify the send to avoid short-writes
            send_confirmation(client_sock)
            # client_sock.send("{}\n".format(msg).encode('utf-8'))
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
        finally:
            client_sock.close()

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        c, addr = self._server_socket.accept()
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
        return c
