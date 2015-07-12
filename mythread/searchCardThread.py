# -*- coding: utf-8 -*-
import threading
from commonlib import constant
from commonlib import commons
from bs4 import BeautifulSoup
import time
import wx
import commonlib.carddatabase as carddatabase
import random
import logging
import traceback
import xlwt


class MyThread(threading.Thread):
    def __init__(self,window,myHttpRequest,cardtheme,cardPrice,nodeItem,searchCardId):
        threading.Thread.__init__(self,)
        self.window = window
        self.myHttpRequest =myHttpRequest
        self.cardtheme = cardtheme
        self.cardPrice = cardPrice
        self.nodeItem = nodeItem
        self.searchCardId = searchCardId
        self.thread_stop = False
        self.database = carddatabase.CardDataBase(self.window.path)
        logging.basicConfig(filename='error.log')
    def run(self):
        userList = []
        soup = BeautifulSoup(str(self.nodeItem))
        uinlist = soup.node['uin']
        uinList = uinlist.split('|')
        for uin in uinList:
            userList.append(uin)
        for user in userList:
            try:
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


                collectThemelist = soup2.changebox['exch'].split(',')
                #print collectThemelist
                cardlist = soup2.find_all('card')
                for item in cardlist:
                    soup3 = BeautifulSoup(str(item))
                    pid = int(soup3.card['id'])
                    cardThemeId = self.database.getCardThemeid(pid)

                    if cardThemeId==self.cardtheme:
                        print 'cardPrice',self.cardPrice
                        if self.cardPrice==u'全部':
                            exchStr = u'对方设置的交换主题:'
                            exchCardTheme = ''
                            hasSetExch = False
                            for collectTheme in collectThemelist:
                                if int(collectTheme)!=0:
                                    hasSetExch = True
                                    exchCardTheme +=self.database.getCardThemeName(int(collectTheme))+','
                            exchStr +=exchCardTheme
                            if not hasSetExch:
                                exchStr = u'对方设置的交换主题:无'
                                exchCardTheme = u'无'
                            wx.CallAfter(self.window.updateCardFriend,user,exchCardTheme)
                            msg = user+','+exchStr
                            wx.CallAfter(self.window.updateLog,msg)
                        else:
                            if self.database.getCardInfo(pid)[2]==self.cardPrice and (self.searchCardId==-1 or pid==self.searchCardId) :
                                exchStr = u'对方设置的交换主题:'
                                exchCardTheme = ''
                                hasSetExch = False
                                for collectTheme in collectThemelist:
                                    if int(collectTheme)!=0:
                                        hasSetExch = True
                                        exchCardTheme +=self.database.getCardThemeName(int(collectTheme))+','
                                exchStr +=exchCardTheme
                                if not hasSetExch:
                                    exchStr = u'对方设置的交换主题:无'
                                    exchCardTheme = u'无'
                                msg = user+','+exchStr
                                wx.CallAfter(self.window.updateCardFriend,user,exchCardTheme)
                                wx.CallAfter(self.window.updateLog,msg)
                        break
                cardlist = []
                if self.thread_stop:
                    return
                time.sleep(0.3)
            except:
                s = traceback.format_exc()
                logging.error(s)
        userList = []
    def stop(self):
        self.thread_stop = True





class SearchCardThread(threading.Thread):
    def __init__(self,window,myHttpRequest,cardtheme,cardPrice,cardDetail):
        threading.Thread.__init__(self,)  
        self.window = window
        self.myHttpRequest =myHttpRequest
        self.cardtheme = cardtheme
        self.cardPrice = cardPrice
        if cardDetail!=-1:
            self.searchCardId = self.window.database.getCardId(cardDetail)
        else:
            self.searchCardId = -1
        self.thread_stop = False
        self.threadList = []
   
    def run(self):
        self.window.database.cu.execute("select * from cardtheme where type=?",(0,))
        result =self.window.database.cu.fetchall()
        logging.basicConfig(filename='error.log')
        #创建搜索的excel表

        for i in range(len(result)):
            print type(result)
            themeItem = random.choice(result)
            result.remove(themeItem)
            if self.thread_stop:
                break
            base_url = commons.getUrl(constant.THEMELISTURL,self.myHttpRequest)
            postData = {
                   'uin':constant.USERNAME,
                   'tid':int(themeItem[1])
            }
            wx.CallAfter(self.window.updateLog,u'搜索正在炼制'+themeItem[2]+u'套卡的卡友')
            try:
                searchCardUserNum = 0;
                while searchCardUserNum<=constant.CARDUSERNUM:
                    if self.thread_stop:
                        break
                    results = self.myHttpRequest.get_response(base_url,postData).read()
                    soup = BeautifulSoup(results)
                    nodeList = soup.find_all('node')
                    #print u'线程个数',len(nodeList)
                    searchCardUserNum +=10*len(nodeList)
                    #wx.CallAfter(self.window.updateLog,u'共有'+str(10*len(nodeList))+u'卡友')
                    for i in range(len(nodeList)):

                        mythread = MyThread(self.window,self.myHttpRequest,self.cardtheme,self.cardPrice,nodeList[i],self.searchCardId)
                        mythread.start()
                        self.threadList.append(mythread)

                    for mythread in self.threadList:
                        mythread.join()
                    mythread = []
            except :
                s = traceback.format_exc()
                logging.error(s)
                continue
        print 'stop'
        wx.CallAfter(self.window.searchComplete)
    def stop(self):
        self.thread_stop = True
        for mythread in self.threadList:
            mythread.thread_stop = True


        