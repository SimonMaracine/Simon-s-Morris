import socket

import pygame

from ..helpers import create_thread, create_socket, Boolean, serialize
from src.networking.package import Package


class Server:
    """Class representing a server object. It communicates with a Client object."""

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.connection = None
        self.waiting_for_conn = False
        self.disconnect = False
        self.hosting = False
        self.sock = None
        self.thread = None
        self.clock = pygame.time.Clock()

        self.to_send: bytes = b"Hallo!"
        self.to_be_received: bytes = serialize(Package(Boolean(False), None, Boolean(False)))

    def prepare(self) -> bool:
        self.sock = create_socket()
        try:
            self.bind()
        except OSError as e:
            print(e)
            return False
        self.sock.settimeout(61)
        self.sock.listen(3)
        print("Server started. Waiting for connection...\n")
        return True

    def run(self) -> bool:
        if not self.waiting_for_conn or self.hosting:
            if not self.prepare():
                return False
            self.thread = create_thread(target=self.wait_for_conns)
            self.thread.start()
            self.waiting_for_conn = True
            return True
        else:
            print("Server already running")
            return False

    def wait_for_conns(self):
        try:
            connection, address = self.sock.accept()
            print("Connected by {}".format(address))
        except OSError as e:
            connection = None
            print(e)
        except socket.timeout as e:
            # print("Socket timed out")
            print(e)
            connection = None

        self.connection = connection

        if connection is not None:
            create_thread(target=self.client).start()
            self.hosting = True
        else:
            print("No connection returned")

        self.waiting_for_conn = False
        self.sock.close()
        print("Socket closed")

    def stop_sock(self):
        sock = create_socket()
        sock.connect((self.host, self.port))
        sock.close()
        print("Listening socket stopped")

    def bind(self):
        self.sock.bind((self.host, self.port))

    def client(self):
        """The send-receive loop with the client."""
        with self.connection as conn:
            while not self.disconnect:
                print("Server working")
                try:
                    conn.send(self.to_send)
                    # print("Sent: {}".format(self.to_send))

                    data: bytes = conn.recv(16384)
                    # try:
                    #     print("Received: {}".format(deserialize(data)))
                    # except EOFError:
                    #     pass
                    self.to_be_received = data

                    if not data:
                        print("Client sent nothing")
                        self.disconnect = True
                except ConnectionAbortedError:
                    print("Client has closed the connection")
                    self.disconnect = True
                except ConnectionResetError:
                    print("Client has probably closed the connection")
                    self.disconnect = True
                # except ConnectionError:
                #     print("An unexpected error occurred")
                #     break
                self.clock.tick(40)

        self.hosting = False
        print("Hosting aborted")

    def send(self, data: bytes):
        self.to_send = data

    def receive(self) -> bytes:
        return self.to_be_received
