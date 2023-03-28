from helpers import get_port, MySocket
import sys
import errno
import shelve
from hashlib import pbkdf2_hmac
import secrets
import base64


if __name__ == '__main__':
    sock = MySocket()
    port = get_port()

    sys.stdout = open('server.log', 'a')

    try:
        sock.bind(('', port))
    except OSError as e:
        if e.errno == errno.EADDRINUSE:
            print('port is not available, using a free port')
            sock.bind(('', 0))
        else:
            raise e
    print('server started')

    sock.listen(0)
    print(f'listening on port {sock.getsockname()[1]}')

    passwords_db = shelve.open('passwords')
    session_tokens_db = shelve.open('session_tokens')

    while True:
        conn, addr = sock.accept()
        print(f'connected client {addr}')

        conn.sendall(b'session token (blank if none): ')
        session_token = conn.recv()
        if session_token:
            session_token = session_token.decode()
            for st, n in session_tokens_db.items():
                if session_token == st:
                    name = n
                    print('authenticated using session token')
                    msg = b''
                    break
            else:
                conn.sendall(b'wrong session token!\n')
                print('got wrong session token')
                continue
        else:
            conn.sendall(b'username: ')
            name = conn.recv().decode()
            conn.sendall(b'password: ')
            password = conn.recv()
            salt_and_hash = passwords_db.get(name)
            if salt_and_hash is None:
                salt = secrets.token_bytes(512 // 8)
                hash = pbkdf2_hmac('sha256', password, salt, 100_000)
                passwords_db[name] = (salt, hash)
                session_token = base64.b64encode(secrets.token_bytes())
                session_tokens_db[session_token.decode()] = name
                print('registered user')
                msg = b'your session token is ' + session_token + b'\n'
            else:
                (salt, hash) = salt_and_hash
                if pbkdf2_hmac('sha256', password, salt, 100_000) == hash:
                    print('authenticated using password')
                    session_token = base64.b64encode(secrets.token_bytes())
                    session_tokens_db[session_token.decode()] = name
                    msg = b'your new session token is ' + session_token \
                        + b'\n'
                else:
                    conn.sendall(b'got wrong password!\n')
                    print('got wrong password')
                    continue

        conn.sendall(b'hello ' + name.encode() + b'\n' + msg)

        while True:
            data = conn.recv()
            if data is None:
                print('disconnected')
                break
            print(f'received {len(data)} bytes')
            conn.sendall(data + b'\n')
            print('sent the data back')
