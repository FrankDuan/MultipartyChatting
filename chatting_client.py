import json
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

        self.r, self.w = None, None
        #self.pipeIn = os.fdopen(r)
        #self.pipeOut = os.fdopen(w, 'w')
        self.parser = MsgParser()
        self.thread = None
        self.run = True
        self.running = False

    def setServer(self, ip, port):
        self.serverIp = ip
        self.serverPort = port

    def connectServer(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((self.serverIp, self.serverPort))
        self.server = server

        joinMsg = self.parser.buildJoinMsg(self.name)
        self.sendMsg(joinMsg)

    def start(self):
        #while self.r:
        #    time.sleep(1)
        print('Starting client!')
        #r, w = os.pipe()
        #self.r, self.w = r, w
        self.connectServer()
        self.thread = threading.Thread(target=self._start)
        self.thread.start()

    def _start(self):
        self.running = True
        while self.run:
            # print('.')
            sockets_list = [self.server]
            read_sockets, write_socket, error_socket = select.select(
                sockets_list, [], [], 1)
            # print('-')
            for socks in read_sockets:
                if socks == self.server:
                    message = socks.recv(2048)
                    #print(message)
                    msg = self.parser.parse(message)
                    if msg:
                        print('Client received msg:', msg)
                        self.onRcvdMsg(msg)
                    ''''''
                else:
                    buffer = os.read(socks, 200)
                    print('send msg', buffer.decode())
                    self.server.send(buffer)

        print('client stopping!')
        self.server.close()
        self.running = False

    def stop(self):
        self.run = False

    def isRunning(self):
        return self.running

    def sendMsg(self, msg):
        msg = json.dumps(msg)
        self.server.send(msg.encode())

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