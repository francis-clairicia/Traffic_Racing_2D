# -*- coding: Utf-8 -*

import socket
import select
import struct
import pickle
from typing import List, Any, Optional
from .thread import threaded_function
from .clock import Clock

STRUCT_FORMAT_PREFIX = ">I"
STRUCT_FORMAT_SIZE = struct.calcsize(STRUCT_FORMAT_PREFIX)

def recv_data(socket: socket.socket) -> bytes:
    try:
        recv_size = struct.unpack(STRUCT_FORMAT_PREFIX, socket.recv(STRUCT_FORMAT_SIZE))[0]
        data = socket.recv(recv_size)
    except:
        data = None
    return data

def send_data(socket: socket.socket, data: bytes) -> None:
    try:
        packed_data = struct.pack(STRUCT_FORMAT_PREFIX, len(data)) + data
        socket.sendall(packed_data)
    except:
        pass

class ServerSocket:

    def __init__(self):
        self.__thread = None
        self.__port = -1
        self.__listen = 0
        self.__socket = None
        self.__clients = list()
        self.__loop = False

    def __del__(self) -> None:
        self.stop()

    def connected(self) -> bool:
        return isinstance(self.__socket, socket.socket)

    def bind(self, port: int, listen: int) -> None:
        self.stop()
        try:
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__socket.bind(("", port))
        except:
            self.__socket = None
        else:
            self.__port = port
        self.listen = listen
        self.__thread = self.__run()

    @property
    def ip(self) -> str:
        return socket.gethostbyname(socket.gethostname())

    @property
    def port(self) -> int:
        return self.__port

    @property
    def listen(self) -> int:
        return self.__listen

    @listen.setter
    def listen(self, value: int) -> int:
        self.__listen = abs(int(value))
        if self.connected():
            self.__socket.listen(self.__listen)

    @property
    def clients(self) -> List[socket.socket]:
        return self.__clients

    @threaded_function
    def __run(self) -> None:
        if not self.connected():
            return
        self.__loop = True
        while self.__loop:
            self.__check_for_connections()
            data_recieved = list()
            for client in self.__clients_to_read():
                data = recv_data(client)
                if isinstance(data, bytes):
                    data_recieved.append((client, data))
            for client_who_send, data in data_recieved:
                for client in filter(lambda client: client != client_who_send, self.clients):
                    send_data(client, data)
        for client in self.clients:
            client.close()
        self.clients.clear()
        self.__socket.close()
        self.__socket = None
        self.__port = -1

    def stop(self) -> None:
        if self.__loop:
            self.__loop = False
            self.__thread.join()
            self.__thread = None

    def __check_for_connections(self) -> None:
        try:
            connections = select.select([self.__socket], [], [], 0.05)[0]
        except:
            connections = list()
        self.clients.extend(connection.accept()[0] for connection in connections)

    def __clients_to_read(self) -> List[socket.socket]:
        try:
            clients_to_read = select.select(self.clients, [], [], 0.05)[0]
        except:
            clients_to_read = list()
        return clients_to_read

class ClientSocket:

    QUIT_MESSAGE = "quit"

    def __init__(self):
        self.__thread = None
        self.__socket = None
        self.__loop = False
        self.__msg = dict()

    def __del__(self) -> None:
        self.stop()

    def connected(self) -> bool:
        return isinstance(self.__socket, socket.socket)

    def connect(self, server_address: str, server_port: int, timeout: int) -> bool:
        self.stop()
        try:
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__socket.settimeout(timeout)
            self.__socket.connect((server_address, server_port))
            self.__socket.settimeout(None)
        except:
            self.__socket = None
        self.__thread = self.__run()
        return self.connected()

    @threaded_function
    def __run(self) -> None:
        if not self.connected():
            return
        self.__loop = True
        while self.__loop:
            try:
                read_socket = bool(len(select.select([self.__socket], [], [], 0.05)[0]) > 0)
            except:
                read_socket = False
            if not read_socket:
                continue
            try:
                data = recv_data(self.__socket)
                msg = pickle.loads(data) if isinstance(data, bytes) else None
            except:
                msg = None
            if not isinstance(msg, dict):
                continue
            print(f"Recieved {msg}")
            self.__msg.update(msg)
        self.__socket.close()
        self.__socket = None

    def stop(self) -> None:
        if self.__loop:
            self.send(ClientSocket.QUIT_MESSAGE)
            self.__loop = False
            self.__thread.join()

    def send(self, msg: str, data: Optional[Any] = None) -> None:
        if self.connected():
            data_dict = {str(msg): data}
            print(f"Sending {data_dict}")
            send_data(self.__socket, pickle.dumps(data_dict))

    def recv(self, msg: str, pop=False) -> bool:
        recieved = bool(msg in self.__msg)
        if pop and recieved:
            self.__msg.pop(msg)
        return recieved

    def get(self, msg: str) -> Any:
        return self.__msg.pop(msg, None)

    def wait_for(self, *messages: str, timeout=1) -> str:
        clock = Clock()
        while self.connected() and not self.recv(ClientSocket.QUIT_MESSAGE, pop=True) and not clock.elapsed_time(timeout * 1000):
            for msg in messages:
                if self.recv(msg):
                    return msg
        send_data(self.__socket, pickle.dumps({ClientSocket.QUIT_MESSAGE, None}))
        return ClientSocket.QUIT_MESSAGE