import socket
import logging
import signal
import sys
import logging
from common.utils import Bet, store_bets, load_bets, has_won
from common.msg_handler import MsgType, recv_message, send_winners


def send_confirmation(socket):
    confirmation = MsgType.SUCCESS
    data = confirmation.value.to_bytes(1, 'big')
    socket.sendall(data)

class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.agencies_finished = {}
        self.waiting_agencies = {}
        self.bets_amount = 0

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

        i = 0
        while True:
            try:
                client_sock = self.__accept_new_connection()
                self.__handle_client_connection(client_sock)
                i += 1
                if 10000 <= self.bets_amount <= 14000 or 26000 <= self.bets_amount <= 30000 or 46000 <= self.bets_amount <= 50000 or 66000 <= self.bets_amount <= 69459:
                    logging.debug(f"Se guardaron {self.bets_amount} bets con {i} conecciones")
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
            # logging.info(f'action: receive_message | result: in_progress')
            msg_type, data = recv_message(client_sock)
            if msg_type == MsgType.BETS:
                bet_header, bets = data
                self.process_bets(bet_header, bets, client_sock)
            elif msg_type == MsgType.NO_MORE_BETS:
                if data in self.agencies_finished:
                    self.agencies_finished[data] = True
            elif msg_type == MsgType.CONSULT_WINNER:
                if data not in self.waiting_agencies:
                    self.waiting_agencies[data] = client_sock
                if self.all_agencies_finished():
                    self.get_winners()
                return
        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
        
        client_sock.close()

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        # logging.info('action: accept_connections | result: in_progress')
        c, addr = self._server_socket.accept()
        # logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
        return c

    def process_bets(self, bet_header, bets, client_sock):
        addr = client_sock.getpeername()
        # logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {bet_header}')
        store_bets(bets)
        if not bet_header.agency in self.agencies_finished:
            self.agencies_finished[bet_header.agency] = False
        self.bets_amount += len(bets)
        # for bet in bets:
        #     logging.info(f'action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}')
        send_confirmation(client_sock)

    def get_winners(self):
        winner_bets = {}
        for bet in load_bets():
            if has_won(bet):
                winner_bets[bet.agency] = winner_bets.get(bet.agency, 0) + 1

        for agency, conn in self.waiting_agencies.items():
            winner_bets[int(agency)] = winner_bets.get(int(agency), 0)
            amount_winners = winner_bets[int(agency)]
            send_winners(conn, amount_winners)
            conn.close()

        logging.info(f'action: sorteo | result: success')

    def all_agencies_finished(self):
        for finished in self.agencies_finished.values():
            if not finished:
                return False
        return True