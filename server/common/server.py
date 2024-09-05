import socket
import logging
import signal
import logging
import os
from multiprocessing import Process, Queue, Pipe, Lock
from common.utils import Bet, store_bets, load_bets, has_won
from common.msg_handler import MsgType, recv_message, send_winners

AMOUNT_AGENCIES = 5

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
        self.childs = []
        self.queue = Queue()
        self.pipes = []
        self.lock = Lock()
        self.agencies = {}
        self.clean = False

    def _handle_sigterm(self, sig, frame):
        """
        Handle SIGTERM signal so the server close gracefully.
        """
        if not self.clean:
            self.clean_up()
        logging.info("action: handle_signal | signal: SIGTERM | result: in_progress")
        self._server_socket.close()
        logging.info("action: handle_signal | signal: SIGTERM | result: success")

    def clean_up(self):
        for child_process, child_conn in self.agencies.values():
            child_conn.close()
            child_process.join()
        logging.debug(f"[Proceso {os.getpid()}] Se cerraron los extremos de pipes de proceso principal, tambien se joinearon los procesos")
        self.clean = True

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
                parent_conn, child_conn = Pipe()

                child_process = Process(
                    target=self.__handle_client_connection,
                    args=(client_sock, self.lock, self.queue, child_conn)
                )

                child_process.start()
                self.agencies[len(self.agencies)+1] = (child_process, parent_conn)

                if len(self.agencies) >= AMOUNT_AGENCIES:
                    self.wait_for_processes_to_finish()
                    # se buscan los ganadores y se envian
                    self.get_winners()
                    self.clean_up()
                
            except OSError as error:
                break

    def __handle_client_connection(self, client_sock, lock, queue, conn):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        # logging.debug("Entre al handle_client")
        try:
            while True:
                # logging.info(f'action: receive_message | result: in_progress')
                msg_type, data = recv_message(client_sock)
                if msg_type == MsgType.BETS:
                    bet_header, bets = data
                    self.handle_bets(bet_header, bets, client_sock, lock)
                elif msg_type == MsgType.NO_MORE_BETS:
                    continue
                elif msg_type == MsgType.CONSULT_WINNER:
                    self.handle_consult(client_sock, data, conn, queue)
                    break
        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
        finally:
            logging.debug(f"[Proceso {os.getpid()}] Cierro el socket del cliente y mi extremo del pipe")
            client_sock.close()
            conn.close()

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

    def handle_bets(self, bet_header, bets, client_sock, lock):
        addr = client_sock.getpeername()
        # logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {bet_header}')
        with lock:
            store_bets(bets)
        send_confirmation(client_sock)

    def get_winners(self):
        winner_bets = {}
        with self.lock:
            for bet in load_bets():
                if has_won(bet):
                    winner_bets[bet.agency] = winner_bets.get(bet.agency, 0) + 1

        for agency, info in self.agencies.items():
            _, parent_conn = info 
            winner_bets[agency] = winner_bets.get(agency, 0)
            amount_winners = winner_bets[agency]
            parent_conn.send_bytes(amount_winners.to_bytes(1, 'big'))

        logging.info(f'action: sorteo | result: success')

    def wait_for_processes_to_finish(self):
        for _ in range(AMOUNT_AGENCIES):
            self.queue.get()

    def handle_consult(self, socket, agency, conn, queue):
        # logging.debug("Entre al handle_consult")
        queue.put(agency)

        bamount_winners = conn.recv_bytes(1)
        amount_winners = int.from_bytes(bamount_winners, 'big')

        send_winners(socket, amount_winners)
