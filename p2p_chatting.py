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
    '''
    def onNewConnection(self, addr, name):
        if self.is_chairman:
            redirect, newAddr = self._allocParentNode(addr)
            if redirect:
                self.server.redirect(addr, name, newAddr)
    '''

    def removeMember(self, addr):
        ip, port = addr
        for name, info in self.members.items():
            if info['ip'] == ip and info['port'] == port:
                del self.members[name]
                print('Member {} removed'.format(name))
                return

    def sendToUpperlayer(self, msg):
        self.msgHandler(msg['name'] + ' : ' + msg['chat'])
        if self.is_chairman:
            return
        self.client.sendMsg(msg)

    def sendToUnderlayer(self, msg):
        self.msgHandler(msg['name'] + ' : ' + msg['chat'])
        self.server.sendMsg(msg)

    def onCtrlMsg(self, msg, addr):
        if msg['type'] == 'join':
            self.onJoinMsg(msg, addr)
        elif msg['type'] == 'redirect':
            self.onRedirectMsg(msg, addr)
        else:
            print(msg, addr)

    def onRedirectMsg(self, msg, addr):
        self.addr = msg['parent_node']
        print('stopping')
        self.client.setServer(self.addr, PORT_NUM)
        self.client.connectServer()
        print('Client reconnect to {}'.format(self.addr))

    def onJoinMsg(self, msg, addr):
        if not self.is_chairman:
            return
        ip, port = addr
        welcome = msg['name'] + ' has joined the chatting, welcome!'
        self.msgHandler(welcome)
        self.broadcastMsg(welcome)
        parentName, parentIP = self._allocParentNode(ip)
        self.members[msg['name']] = {'ip': ip, 'port': port}
        if parentIP:
            print('Redirect', msg['name'], 'to', parentName)
            time.sleep(2)
            self.server.redirect(addr, name, parentIP)

    def _allocParentNode(self, ip):
        ip = ip.split('.')
        for name, info in self.members.items():
            addr = info['ip'].split('.')
            if ip[0] == addr[0] and ip[1] == addr[1] and ip[2] == addr[2]:
                return name, info['ip']
        return None, None


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
