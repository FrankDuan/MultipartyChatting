import os
import socket
import select
import sys

import threading
import time

from msg_parser import MsgParser


class ChattingClient:
    def __init__(self, name, msgHandler, server_ip, server_port):
        self.server = None
        self.name = name
        self.serverIp = server_ip
        self.serverPort = server_port
        self.msgHandler = msgHandler

        r, w = os.pipe()
        self.r, self.w = r, w
        self.pipeIn = os.fdopen(r)
        self.pipeOut = os.fdopen(w, 'w')
        self.parser = MsgParser()
        self.thread = threading.Thread(target=self._start)
        self.run = True

    def setServer(self, ip, port):
        pass

    def start(self):
        self.thread.start()
        joinMsg = self.parser.buildJoinMsg(self.name)
        self.sendMsg(joinMsg)

    def _start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((self.serverIp, self.serverPort))
        self.server = server

        while self.run:
            sockets_list = [server, self.r]
            read_sockets, write_socket, error_socket = select.select(
                sockets_list, [], [], 1)
            for socks in read_sockets:
                if socks == server:
                    message = socks.recv(2048)
                    #print(message)
                    msg = self.parser.parse(message)
                    if msg:
                        print('Client received msg:', msg)
                        self.onRcvdMsg(msg)
                else:
                    buffer = os.read(socks, 200)
                    print('send msg', buffer.decode())
                    server.send(buffer)
        self.server.close()

    def stop(self):
        self.run = False

    def sendMsg(self, msg):
        self.pipeOut.write(msg)
        os.write(self.w, msg.encode())

    def onRcvdMsg(self, msg):
        if msg['type'] == 'chat':
            self.msgHandler.sendToUnderlayer(msg)
        else:
            self.msgHandler.onCtrlMsg(msg, self.server)


class TestMsgHandler:
    def sendToUnderlayer(self, msg):
        print('sendToUnderlayer:', msg)

    def onCtrlMsg(self, msg, connection):
        pass


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Correct usage: script, IP address, port number, name")
        exit()
    IP_address = str(sys.argv[1])
    Port = int(sys.argv[2])
    name = str(sys.argv[3])
    client = ChattingClient(name, TestMsgHandler, IP_address, Port)
    client.start()
    msg = MsgParser.buildChatMsg(name, 'Hello, Alice!')
    client.sendMsg(msg)
    time.sleep(200)
    client.stop()