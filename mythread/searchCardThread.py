# -*- coding: utf-8 -*-
import threading
from commonlib import constant
from commonlib import commons
from bs4 import BeautifulSoup
import time
import wx
import commonlib.carddatabase as carddatabase


class MyThread(threading.Thread):
    def __init__(self,window,myHttpRequest,cardtheme,cardPrice,nodeItem):
        threading.Thread.__init__(self,)
        self.window = window
        self.myHttpRequest =myHttpRequest
        self.cardtheme = cardtheme
        self.cardPrice = cardPrice
        self.nodeItem = nodeItem
        self.thread_stop = False
        self.database = carddatabase.CardDataBase(self.window.path)
    def run(self):
        userList = []
        soup = BeautifulSoup(str(self.nodeItem))
        uinlist = soup.node['uin']
        uinList = uinlist.split('|')
        for uin in uinList:
            userList.append(uin)
        for user in userList:
            print 'search user',user
            if user=='':
                continue
            base_url = commons.getUrl(constant.CARDLOGINURL,self.myHttpRequest)
            postData = {
               'uin':constant.USERNAME,
               'opuin':user,
            }
            result = self.myHttpRequest.get_response(base_url,postData).read()
            soup = BeautifulSoup(result)
            soup2 = BeautifulSoup(str(soup.changebox))
            cardlist = soup2.find_all('card')
            for item in cardlist:
                soup3 = BeautifulSoup(str(item))
                pid = int(soup3.card['id'])
                cardThemeId = self.database.getCardThemeid(pid)

                if cardThemeId==self.cardtheme:
                    print 'cardPrice',self.cardPrice
                    if self.cardPrice==u'全部':
                        print u'你搜索的是全部'
                        wx.CallAfter(self.window.updateLog,user)
                    else:
                        if self.database.getCardInfo(pid)[2]==self.cardPrice:
                            wx.CallAfter(self.window.updateLog,user)
                    # myfile = open('1.txt','a')
                    # myfile.write('QQ'+str(user)+'\n')
                    # myfile.close()
                    break
            if self.thread_stop:
                return
            time.sleep(0.3)

    def stop(self):
        self.thread_stop = True





class SearchCardThread(threading.Thread):
    def __init__(self,window,myHttpRequest,cardtheme,cardPrice):
        threading.Thread.__init__(self,)  
        self.window = window
        self.myHttpRequest =myHttpRequest
        self.cardtheme = cardtheme
        self.cardPrice = cardPrice
        self.thread_stop = False
        self.threadList = []
   
    def run(self):
        self.window.database.cu.execute("select * from cardtheme where type=?",(0,))
        result =self.window.database.cu.fetchall()

        for themeItem in result:
            if self.thread_stop:
                return
            base_url = commons.getUrl(constant.THEMELISTURL,self.myHttpRequest)
            postData = {
                   'uin':constant.USERNAME,
                   'tid':int(themeItem[1])
            }
            wx.CallAfter(self.window.updateLog,u'正在搜索'+themeItem[2]+u'套卡')
            try:
                result = self.myHttpRequest.get_response(base_url,postData).read()
                soup = BeautifulSoup(result)

                nodeList = soup.find_all('node')
                print u'线程个数',len(nodeList)
                for i in range(len(nodeList)):

                    mythread = MyThread(self.window,self.myHttpRequest,self.cardtheme,self.cardPrice,nodeList[i])
                    mythread.start()
                    self.threadList.append(mythread)

                for mythread in self.threadList:
                    mythread.join()
            except Exception:
                print 'error'
                continue
        
    def stop(self):
        self.thread_stop = True
        print 'press top'
        for mythread in self.threadList:
            mythread.thread_stop = True


        