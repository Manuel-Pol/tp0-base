import socket
import logging
import signal
import sys
from common.utils import Bet, store_bets
from common.package import Package, MAX_STR_SIZE_BYTES, MAX_NUMBER_SIZE_BYTES, MAX_IDENTITY_SIZE_BYTES

def recv_data(socket):
    data_packet_size = bytearray()
    data = bytearray()
    while len(data_packet_size) < 1:
        packet = socket.recv(1)
        if not packet:
            break 
        data_packet_size += packet
    
    package_size = int.from_bytes(data_packet_size, 'big')
    while len(data) < package_size:
        packet = socket.recv(package_size)
        if not packet:
            break
        data += packet
    
    return data


def send_data(socket):
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
        self._server_socket.close()

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
            logging.info(f'action: receive_message | result: in_progress')
            data = recv_data(client_sock)
            package = Package.deserialize(data)
            addr = client_sock.getpeername()
            logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {package}')
            bet = Bet("1", package.name, package.lastname, str(package.document), package.birthday, str(package.number))
            store_bets([bet])
            logging.info(f'action: apuesta_almacenada | result: success | dni: {package.document} | numero: {package.number}')
            send_data(client_sock)
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
