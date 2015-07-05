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
        self.priceList = []
        #-------------炉子操作----------
        sb  = wx.StaticBox(self,label = u'需要搜索的套卡')
        self.sloveOperateSizer = wx.StaticBoxSizer(sb,wx.HORIZONTAL)
        self.cardLabel = wx.StaticText(self,-1,u'卡片')
        self.collectThemeChoice = wx.Choice(self,-1,(50,400),wx.DefaultSize,self.getCollectTheme())
        self.collectThemeChoice.Bind(wx.EVT_CHOICE,self.onCollectThemeChoice)
        self.cardPriceLabel = wx.StaticText(self,-1,u'面值')
        self.searchCardPriceChoice = wx.Choice(self,-1,(50,400),wx.DefaultSize,[])
        self.searchBt = wx.Button(self,-1,u'搜索')
        self.searchStop = wx.Button(self,-1,u'停止')
        self.searchBt.Bind(wx.EVT_BUTTON, self.searchTheme)
        self.searchStop.Bind(wx.EVT_BUTTON, self.stopSearchTheme)
        self.sloveOperateSizer.Add(self.cardLabel,0,wx.ALL,5)
        self.sloveOperateSizer.Add(self.collectThemeChoice,0,wx.ALL,5)
        self.sloveOperateSizer.Add(self.cardPriceLabel,0,wx.ALL,5)
        self.sloveOperateSizer.Add(self.searchCardPriceChoice,0,wx.ALL,5)
        self.sloveOperateSizer.Add(self.searchBt,0,wx.ALL,5)
        self.sloveOperateSizer.Add(self.searchStop,0,wx.ALL,5)

        self.msgLog = wx.TextCtrl(self,-1,size=(900,200),style=wx.TE_MULTILINE)

        self.searchStop.Enable(False)

        #---------------总的布局----------
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.sloveOperateSizer, 0, wx.EXPAND)
        self.sizer.Add(self.msgLog, 1, wx.EXPAND)
#         #Layout sizers
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.Center()
        self.Show(True)

        configFile = open('config.ini','r')
        constant.CARDUSERNUM = int(configFile.readline().split('=')[1])
        configFile.close()



    '''选择搜索套卡事件
    '''
    def onCollectThemeChoice(self,e):
        self.priceList = []
        self.priceList.append(u'全部')
        self.database.cu.execute("select price from cardinfo where  themeid=?",
                                 (int(self.themeIdList[self.collectThemeChoice.GetSelection()]),))
        result =self.database.cu.fetchall()
        for item in result:
            price = item[0]
            if not str(price) in self.priceList:
                self.priceList.append(str(price))
        self.searchCardPriceChoice.SetItems(self.priceList)
        self.searchCardPriceChoice.SetSelection(0)

    '''搜索主题
    '''
    def searchTheme(self,e):

        self.searchThread = searchCardThread.SearchCardThread(self,self.myHttpRequest,
                                                         int(self.themeIdList[self.collectThemeChoice.GetSelection()]),
                                                              self.searchCardPriceChoice.GetStringSelection())
        self.searchThread.start()
        self.searchStop.Enable(True)
        self.searchBt.Enable(False)
        self.msgLog.SetValue("")
        

    '''停止搜索
    '''
    def stopSearchTheme(self,e):
        self.searchThread.stop()
        self.searchStop.Enable(False)
        self.searchBt.Enable(True)

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
        return themeName
    
