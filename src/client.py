from helpers import get_port, MySocket

DEFAULT_HOST = '127.0.0.1'


def get_host():
    host = input(f'enter server host ({DEFAULT_HOST}): ')
    if not host:
        return DEFAULT_HOST
    else:
        return host


if __name__ == '__main__':
    host = get_host()
    port = get_port()
    sock = MySocket()
    sock.setblocking(True)
    sock.connect((host, port))
    print(f'connected to {host}:{port}')

    while True:
        data = sock.recv()
        print(data.decode(), end='')

        msg = input().encode()
        sock.sendall(msg)
