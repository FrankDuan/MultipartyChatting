import json
import traceback

class MsgParser:
    def __init__(self):
        pass

    @classmethod
    def parse(cls, msgBytes):
        msg = msgBytes.decode('utf-8')
        try:
            msg = json.loads(msg)
            if type(msg) is str:
                msg = json.loads(msg)

            if type(msg) is dict:
                return msg
            else:
                print('Failed to load json: ', msg)
                return None
        except:
            print(msgBytes.decode('utf-8'))
            traceback.print_exc()
            return None

    @classmethod
    def buildRedirectMsg(cls, newAddr):
        msg = {'type': 'redirect', 'parent_node': newAddr}
        msg = json.dumps(msg)
        return msg

    @classmethod
    def buildJoinMsg(cls, name):
        msg = {'type': 'join', 'name': name}
        msg = json.dumps(msg)
        return msg

    @classmethod
    def buildChatMsg(cls, name, chat):
        msg = {'type': 'chat', 'name': name, 'chat': chat}
        msg = json.dumps(msg)
        return msg

    @classmethod
    def buildLeaveMsg(cls, name):
        msg = {'type': 'leave', 'name': name}
        msg = json.dumps(msg)
        return msg
