import json
import select
import socket
import sys
import threading
import time
import traceback

from msg_parser import MsgParser


class ChattingServer:
    def __init__(self, msgHandler, ip_addr, listenOnPort):
        self.msgHandler = msgHandler
        self.connections = {}
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.run = True
        self.serverThread = None
        self.ip = ip_addr
        self.port = listenOnPort

    def start(self):
        self.serverThread = threading.Thread(target=self._run)
        self.serverThread.start()

    def _run(self):
        self.server.bind(('0.0.0.0', self.port))
        self.server.listen(self.port)
        while self.run:
            ready = select.select([self.server], [], [], 1)
            if not ready[0]:
                continue
            conn, addr = self.server.accept()
            self.connections[conn] = {'addr': addr, 'parser': MsgParser()}
            print(addr, " connected")
            thread = threading.Thread(target=self.clientThread,
                                      args=(conn,))
            thread.start()

    def clientThread(self, conn):
        #conn.send(str.encode("Welcome to this chatting!"))
        while self.run:
            try:
                ready = select.select([conn], [], [], 1)
                if not ready[0]:
                    continue
                data = conn.recv(2048)
                if data:
                    msg = self.connections[conn]['parser'].parse(data)
                    if msg:
                        # print('Server received msg:', msg)
                        self.onRcvdMsg(msg, conn)
                else:
                    self.remove(conn)
            except:
                if msg:
                    print(msg)
                traceback.print_exc()
                continue

    def broadcast(self, message, connection):
        toRemove = []
        for client in self.connections:
            if client != connection:
                try:
                    msg = json.dumps(message)
                    client.send(msg.encode())
                except:
                    traceback.print_exc()
                    client.close()
                    toRemove.append(client)

        for i in toRemove:
            self.remove(i)

    def remove(self, connection):
        if connection in self.connections:
            self.msgHandler.removeMember(self.connections[connection]['addr'])
            del self.connections[connection]

    def stop(self):
        self.run = False

    def sendMsg(self, msg):
        self.broadcast(msg, None)

    def redirect(self, addr, name, newAddr):
        # print(addr, self.connections)
        for conn, info in self.connections.items():
            if info['addr'] == addr:
                msg = MsgParser.buildRedirectMsg(newAddr)
                conn.send(msg.encode())
                # print('Redirect msg sent!')

    def onRcvdMsg(self, msg, conn):
        if msg['type'] == 'chat':
            self.msgHandler.sendToUpperlayer(msg)
            self.broadcast(msg, conn)
        else:
            self.msgHandler.onCtrlMsg(msg, self.connections[conn]['addr'])


class TestMsgHandler:
    def sendToUpperlayer(self, msg):
        print('sendToUpperlayer:', msg)

    def onCtrlMsg(self, msg, connection):
        print('Ctrl msg:', msg)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Correct usage: script, IP address, port number")
        exit()

    IP_address = str(sys.argv[1])
    Port = int(sys.argv[2])
    server = ChattingServer(TestMsgHandler, Port)
    server.start()
    time.sleep(300)
    server.stop()
