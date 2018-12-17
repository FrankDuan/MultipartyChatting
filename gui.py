import wx
import time
from threading import Timer

from p2p_chatting import P2pChatting


class UserNameDialog(wx.Dialog):

    def __init__(self, *args, **kw):
        super(UserNameDialog, self).__init__(*args, **kw)

        self.InitUI()
        self.SetSize((250, 200))
        self.SetTitle("Input Your Name")
        self.name = ''
        self.nameCtrl = None

    def InitUI(self):

        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.nameCtrl = wx.TextCtrl()
        hbox1.Add(self.nameCtrl, flag=wx.LEFT, border=5)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self, label='OK')
        closeButton = wx.Button(self, label='Cancel')
        hbox2.Add(okButton)
        hbox2.Add(closeButton, flag=wx.LEFT, border=5)

        vbox.Add(hbox1, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        vbox.Add(hbox2, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)

        self.SetSizer(vbox)

        okButton.Bind(wx.EVT_BUTTON, self.OnClose)
        closeButton.Bind(wx.EVT_BUTTON, self.OnClose)

    def OnClose(self, e):
        self.name = self.nameCtrl.GetValue()
        self.Destroy()


class GUI(wx.Frame):

    def __init__(self, parent, title):
        super(GUI, self).__init__(parent, title=title, size=(800, 600))
        self.chatting = None
        self.user_name = ''
        self.addrCtrl = None
        self.rcvdCtrl = None
        self.sendCtrl = None
        self.InitUI()
        self.Centre()
        self.Show()
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update, self.timer)
        self.lines = []

    def InitUI(self):
        panel = wx.Panel(self)

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        fgs = wx.FlexGridSizer(3, 2, 9, 25)

        addr = wx.StaticText(panel, label="Chairman Address:")
        MsgRcvd = wx.StaticText(panel, label="Message Received:")
        MsgSent = wx.StaticText(panel, label="Message to Send:")

        tc1 = wx.TextCtrl(panel)
        tc2 = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        tc3 = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)

        fgs.AddMany([(addr), (tc1, 1, wx.EXPAND), (MsgRcvd),
            (tc2, 1, wx.EXPAND), (MsgSent, 1, wx.EXPAND), (tc3, 1, wx.EXPAND)])

        fgs.AddGrowableRow(1, 1)
        fgs.AddGrowableCol(1, 1)

        hbox.Add(fgs, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)
        panel.SetSizer(hbox)

        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        tc1.Bind(wx.EVT_KILL_FOCUS, self.OnEnterAddr)
        tc3.Bind(wx.EVT_TEXT_ENTER, self.OnSendMsg)

        self.msgOutBox = tc2

    def setUserName(self, name):
        self.user_name = name

    def OnCloseWindow(self, event):
        if self.chatting:
            self.chatting.stop()
        self.Destroy()

    def OnEnterAddr(self, event):
        t = event.GetEventObject()
        addr = t.GetValue()
        if not addr:
            return

        print('Address: %s\n' % addr)
        if self.chatting is None:
            self.chatting = P2pChatting(self.user_name, self.OnRecvedMsg)
        self.chatting.setAddr(addr)
        self.chatting.start()
        self.timer.Start(100)

    def OnSendMsg(self, event):
        t = event.GetEventObject()
        msg = t.GetValue()
        t.SetValue('')
        print('Msg: %s\n' % msg)

        if self.chatting:
            self.chatting.broadcastMsg(msg)

    def update(self, data):
        for line in self.lines:
            self.msgOutBox.AppendText(line)
        self.lines = []
        self.timer.Start(100)

    def OnRecvedMsg(self, msg):
        # Resart the timer
        #t = Timer(1, self.AddText)
        #t.start()

        #timeStamp = str(time.time())
        self.lines.append(msg + "\n")

        '''
        # Work out if we're at the end of the file
        currentCaretPosition = self.msgOutBox.GetInsertionPoint()
        currentLengthOfText = self.msgOutBox.GetLastPosition()
        if currentCaretPosition != currentLengthOfText:
            self.holdingBack = True
        else:
            self.holdingBack = False

        timeStamp = str(time.time())

        # If we're not at the end of the file, we're holding back
        if self.holdingBack:
            print("%s FROZEN"%(timeStamp))
            self.msgOutBox.Freeze()
            (currentSelectionStart, currentSelectionEnd) = self.msgOutBox.GetSelection()
            self.msgOutBox.AppendText(timeStamp+"\n")
            self.msgOutBox.SetInsertionPoint(currentCaretPosition)
            self.msgOutBox.SetSelection(currentSelectionStart, currentSelectionEnd)
            self.msgOutBox.Thaw()
        else:
            print("%s THAWED"%(timeStamp))
            self.msgOutBox.AppendText(timeStamp+"\n")

        '''

def main():

    app = wx.App()
    ex = GUI(None, title='MultipartyChatting')
    ex.Show()
    # Create text input
    dlg = wx.TextEntryDialog(ex, '', 'Your Name')
    dlg.SetValue("")
    if dlg.ShowModal() != wx.ID_OK:
        dlg.Destroy()
        exit(0)
    ex.setUserName(dlg.GetValue())
    dlg.Destroy()
    app.MainLoop()


if __name__ == '__main__':
    main()
