import socket

def is_host_reachable(host, port):
    try:
        with socket.create_connection((host, port), timeout = 2):
            return True
    except OSError:
        return False
    