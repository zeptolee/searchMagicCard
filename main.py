# -*- coding: utf-8 -*-
import wx
from mythread import searchCardThread
from commonlib import constant

           
class Main(wx.Frame):
    
    def __init__(self, parent, title,myHttpRequest,database,path):
        wx.Frame.__init__(self, parent, title=title, size=(930,600))
        self.myHttpRequest = myHttpRequest
        self.database = database
        #脚本路径
        self.path = path
        #主题列表
        self.themeIdList = []
        self.themeNameList = []
        self.seachThemeIndex = -1
        self.priceList = []
        #搜索到的卡友列表
        self.cardFriendList = []

        self.ignoreEvtText = False
        #-------------炉子操作----------
        sb  = wx.StaticBox(self,label = u'需要搜索的套卡')
        self.sloveOperateSizer = wx.StaticBoxSizer(sb,wx.HORIZONTAL)
        self.cardLabel = wx.StaticText(self,-1,u'套卡')
        self.collectThemeChoice = wx.ComboBox(self,-1,pos=wx.DefaultPosition,size=wx.DefaultSize,choices=self.getCollectTheme(),style=wx.CB_DROPDOWN)
        self.collectThemeChoice.Bind(wx.EVT_COMBOBOX ,self.onCollectThemeChoice)
        self.collectThemeChoice.Bind(wx.EVT_TEXT_ENTER ,self.onCollectThemeSearch)
        self.collectThemeChoice.Bind(wx.EVT_TEXT, self.EvtText)
        self.collectThemeChoice.Bind(wx.EVT_CHAR, self.EvtChar)
        self.cardPriceLabel = wx.StaticText(self,-1,u'面值')
        self.searchCardPriceChoice = wx.Choice(self,-1,(50,400),wx.DefaultSize,[])
        self.searchCardPriceChoice.Bind(wx.EVT_CHOICE,self.onCardPriceChoice)
        self.detailCardLabel = wx.StaticText(self,-1,u'卡片')
        self.detailCardChoice = wx.Choice(self,-1,(50,400),wx.DefaultSize,[])
        self.detailCardChoice.Enable(False)
        self.searchBt = wx.Button(self,-1,u'搜索')
        self.searchStop = wx.Button(self,-1,u'停止')
        self.searchBt.Bind(wx.EVT_BUTTON, self.searchTheme)
        self.searchStop.Bind(wx.EVT_BUTTON, self.stopSearchTheme)
        self.sloveOperateSizer.Add(self.cardLabel,0,wx.ALL,5)
        self.sloveOperateSizer.Add(self.collectThemeChoice,0,wx.ALL,5)
        self.sloveOperateSizer.Add(self.cardPriceLabel,0,wx.ALL,5)
        self.sloveOperateSizer.Add(self.searchCardPriceChoice,0,wx.ALL,5)
        self.sloveOperateSizer.Add(self.detailCardLabel,0,wx.ALL,5)
        self.sloveOperateSizer.Add(self.detailCardChoice,0,wx.ALL,5)
        self.sloveOperateSizer.Add(self.searchBt,0,wx.ALL,5)
        self.sloveOperateSizer.Add(self.searchStop,0,wx.ALL,5)

        self.msgLog = wx.TextCtrl(self,-1,size=(900,200),style=wx.TE_MULTILINE)

        self.searchStop.Enable(False)


        #---------------超链接-----------
        self.cardFriendLinkSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.hyper = wx.HyperlinkCtrl(self,-1,u"卡友链接", pos=(100, 100),
                                  url="http://appimg2.qq.com/card/index_v3.html#opuin=")
        self.userIdChoice = wx.Choice(self,-1,(50,400),wx.DefaultSize,[])
        self.userIdChoice.Bind(wx.EVT_CHOICE,self.onCardUserChoice)
        self.cardFriendLinkSizer.Add(self.hyper,0,wx.ALL,5)
        self.cardFriendLinkSizer.Add(self.userIdChoice,0,wx.ALL,5)

        #---------------总的布局----------
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.sloveOperateSizer, 0, wx.EXPAND)
        self.sizer.Add(self.cardFriendLinkSizer, 0, wx.EXPAND)
        self.sizer.Add(self.msgLog, 1, wx.EXPAND)
#         #Layout sizers
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.Center()
        self.Show(True)
        try:
            configFile = open('config.ini','r')
            constant.CARDUSERNUM = int(configFile.readline().split('=')[1])
            configFile.close()
        except IOError:
            print 'file not exist'


    '''选择搜索套卡事件
    '''
    def onCollectThemeChoice(self,e):
        self.priceList = []
        self.priceList.append(u'全部')
        self.seachThemeIndex = self.collectThemeChoice.GetSelection()
        self.database.cu.execute("select price from cardinfo where  themeid=?",
                                 (int(self.themeIdList[self.seachThemeIndex]),))
        result =self.database.cu.fetchall()
        for item in result:
            price = item[0]
            if not str(price) in self.priceList:
                self.priceList.append(str(price))
        self.searchCardPriceChoice.SetItems(self.priceList)
        self.searchCardPriceChoice.SetSelection(0)
        self.ignoreEvtText = True
        e.Skip()

    def onCollectThemeSearch(self,e):
        self.priceList = []
        self.priceList.append(u'全部')
        self.database.cu.execute("select price from cardinfo where  themeid=?",
                                 (int(self.themeIdList[self.seachThemeIndex]),))
        result =self.database.cu.fetchall()
        for item in result:
            price = item[0]
            if not str(price) in self.priceList:
                self.priceList.append(str(price))
        self.searchCardPriceChoice.SetItems(self.priceList)
        self.searchCardPriceChoice.SetSelection(0)
        self.ignoreEvtText = True
        e.Skip()

    def EvtChar(self, event):
        if event.GetKeyCode() == 8:
            self.ignoreEvtText = True
        event.Skip()


    def EvtText(self, event):
        if self.ignoreEvtText:
            self.ignoreEvtText = False
            return
        currentText = event.GetString()
        print currentText
        found = False
        for i,choice in enumerate(self.themeNameList) :
            if choice.startswith(currentText):
                self.ignoreEvtText = True
                self.collectThemeChoice.SetValue(choice)
                self.collectThemeChoice.SetInsertionPoint(len(currentText))
                self.collectThemeChoice.SetMark(len(currentText), len(choice))
                self.seachThemeIndex = i
                found = True
                break
        if not found:
            event.Skip()


    '''选择卡片价格事件
    '''
    def onCardPriceChoice(self,e):
        if self.searchCardPriceChoice.GetSelection()!=0:
            self.detailCardChoice.Enable(True)
            self.database.cu.execute("select name from cardinfo where  themeid=? and price=?",
                                 (int(self.themeIdList[self.seachThemeIndex]),
                                  int(self.searchCardPriceChoice.GetStringSelection())))
            result =self.database.cu.fetchall()
            cardNameList = []
            cardNameList.append(u'全部')
            for item in result:
                cardName = item[0]
                cardNameList.append(cardName)
            self.detailCardChoice.SetItems(cardNameList)
            self.detailCardChoice.SetSelection(0)
        else:
            self.detailCardChoice.Enable(False)


    '''搜索主题
    '''
    def searchTheme(self,e):
        self.selectNum = -1
        self.cardFriendList=[]
        try:
            cardDetail = self.detailCardChoice.GetStringSelection()
            if cardDetail==u'全部' or cardDetail=='':
                cardDetail = -1
        except:
            cardDetail = -1
        self.searchThread = searchCardThread.SearchCardThread(self,self.myHttpRequest,
                                                         int(self.themeIdList[self.seachThemeIndex]),
                                                              self.searchCardPriceChoice.GetStringSelection(),
                                                              cardDetail)
        self.searchThread.start()
        self.searchStop.Enable(True)
        self.searchBt.Enable(False)
        self.collectThemeChoice.Enable(False)
        self.detailCardChoice.Enable(False)
        self.searchCardPriceChoice.Enable(False)
        self.msgLog.SetValue("")
        e.Skip()

    '''停止搜索
    '''
    def stopSearchTheme(self,e):
        self.searchThread.stop()
        self.searchStop.Enable(False)
        self.searchBt.Enable(True)
        self.collectThemeChoice.Enable(True)
        self.detailCardChoice.Enable(True)
        self.searchCardPriceChoice.Enable(True)

    '''更新操作日志
    '''
    def updateLog(self,msg):
        self.msgLog.AppendText(msg+'\n')

    '''
    获取要收集的主题
    '''
    def getCollectTheme(self):
        themeName = []
        self.database.cu.execute("select * from cardtheme order by diff ASC ")
        result = self.database.cu.fetchall()
        for themeItem in result:
            themeName.append('['+str(themeItem[3])+u"星]"+themeItem[2])
            self.themeIdList.append(themeItem[1])
            self.themeNameList.append(themeItem[2])
        return themeName

    '''更新搜索到的卡友信息
    '''
    def updateCardFriend(self,user):

        self.cardFriendList.append(user)
        self.userIdChoice.SetItems(self.cardFriendList)
        self.userIdChoice.SetSelection(self.selectNum)
    '''卡友列表被选择时
    '''
    def onCardUserChoice(self,e):
        self.selectNum = self.userIdChoice.GetSelection()
        self.hyper.SetURL(r'http://appimg2.qq.com/card/index_v3.html#opuin='+str(self.cardFriendList[self.selectNum]))
        e.Skip()
