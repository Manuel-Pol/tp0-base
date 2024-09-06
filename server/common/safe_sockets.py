def safe_read(socket, n_bytes):
    data = bytearray()
    while len(data) < n_bytes:
        packet = socket.recv(n_bytes)
        if not packet:
            return None
        data += packet
    return data

def safe_write(socket, n_bytes):
    pass