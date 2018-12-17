import sys
import time

from chatting_client import ChattingClient
from chatting_server import ChattingServer
from msg_parser import MsgParser

PORT_NUM = 60860


class P2pChatting(object):

    def __init__(self, name, receivedMsgHandler):
        self.my_name = name
        self.is_chairman = False
        self.members = {}
        self.msgHandler = receivedMsgHandler
        self.client = None
        self.server = None
        self.addr = None
        self.listen_port = PORT_NUM

    def setUserName(self, name):
        self.my_name = name

    def setListenPort(self, port):
        self.listen_port = port

    def setAddr(self, addr):
        self.addr = addr
        if addr == 'localhost' or addr == '127.0.0.1':
            self.is_chairman = True
        else:
            self.is_chairman = False

    def start(self):
        self.stop()
        self.server = ChattingServer(self, self.addr, self.listen_port)
        self.server.start()

        if not self.is_chairman:
            self.client = ChattingClient(self.my_name, self, self.addr, PORT_NUM)
            self.client.start()

    def stop(self):
        if self.server:
            self.server.stop()
        if self.client:
            self.client.stop()

    def broadcastMsg(self, msg):
        self.msgHandler(self.my_name + ' : ' + msg)
        msg = MsgParser.buildChatMsg(self.my_name, msg)
        if self.client:
            self.client.sendMsg(msg)
        if self.server:
            self.server.sendMsg(msg)

    def onNewConnection(self, addr, name):
        if self.is_chairman:
            redirect, newAddr = self._allocParentNode(addr)
            if redirect:
                self.server.redirect(addr, name, newAddr)

    def _allocParentNode(self, addr):
        return False, None

    def sendToUpperlayer(self, msg):
        self.msgHandler(msg['name'] + ' : ' + msg['chat'])
        if self.is_chairman:
            return
        self.client.sendMsg(msg)

    def sendToUnderlayer(self, msg):
        self.msgHandler(msg['name'] + ' : ' + msg['chat'])
        self.server.sendMsg(msg)

    def onCtrlMsg(self, msg, addr):
        pass


class TestMsgHandler:
    def OnRecvedMsg(self, msg):
        print('Received Msg:', msg)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Correct usage: script, IP address, port number, name")
        exit()
    IP_address = str(sys.argv[1])
    name = str(sys.argv[2])
    testHandler = TestMsgHandler()
    chatting = P2pChatting(name, testHandler.OnRecvedMsg)
    chatting.setAddr(IP_address)
    if len(sys.argv) == 4:
        portNum = int(sys.argv[3])
        chatting.setListenPort(portNum)
    chatting.start()
    print('Input your msg:')
    while True:
        data = sys.stdin.readline().strip()
        if data != 'exit' and data != 'quit':
            chatting.broadcastMsg(data)
        else:
            break
    print('Ending!')
    chatting.stop()
