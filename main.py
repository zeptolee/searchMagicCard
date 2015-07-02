# -*- coding: utf-8 -*-
import wx
from mythread import searchCardThread

           
class Main(wx.Frame):
    
    def __init__(self, parent, title,myHttpRequest,database):
        wx.Frame.__init__(self, parent, title=title, size=(930,600))
        self.myHttpRequest = myHttpRequest
        self.database = database
        #主题列表
        self.themeIdList = []

        #-------------炉子操作----------
        sb  = wx.StaticBox(self,label = u'需要搜索的套卡')
        self.sloveOperateSizer = wx.StaticBoxSizer(sb,wx.HORIZONTAL)
        self.cardLabel = wx.StaticText(self,-1,u'卡片')
        self.collectThemeChoice = wx.Choice(self,-1,(50,400),wx.DefaultSize,self.getCollectTheme())
        self.searchBt = wx.Button(self,-1,u'搜索')
        self.searchBt.Bind(wx.EVT_BUTTON, self.searchTheme)
        self.sloveOperateSizer.Add(self.cardLabel,0,wx.ALL,5)
        self.sloveOperateSizer.Add(self.collectThemeChoice,0,wx.ALL,5)
        self.sloveOperateSizer.Add(self.searchBt,0,wx.ALL,5)


        self.msgLog = wx.TextCtrl(self,-1,size=(900,200))



        #---------------总的布局----------
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.sloveOperateSizer, 0, wx.EXPAND)
        self.sizer.Add(self.msgLog, 1, wx.EXPAND)
#         #Layout sizers
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.Center()
        self.Show(True)



    def searchTheme(self,e):

        searchThread = searchCardThread.SearchCardThread(self,self.myHttpRequest,
                                                         int(self.themeIdList[self.collectThemeChoice.GetSelection()]))
        searchThread.start()
        


    def updateLog(self,msg):
        self.msgLog.AppendText(msg)

    '''
    获取要收集的主题
    '''
    def getCollectTheme(self):
        themeName = []
        self.database.cu.execute("select * from cardtheme")
        result = self.database.cu.fetchall()
        for themeItem in result:
            themeName.append('['+str(themeItem[3])+u"星]"+themeItem[2])
            self.themeIdList.append(themeItem[1])
        return themeName
    
