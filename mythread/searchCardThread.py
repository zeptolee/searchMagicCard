# -*- coding: utf-8 -*-
import threading
from commonlib import constant
from commonlib import commons
from bs4 import BeautifulSoup
import time
import wx
class SearchCardThread(threading.Thread):
    def __init__(self,window,myHttpRequest,cardtheme):
        threading.Thread.__init__(self,)  
        self.window = window
        self.myHttpRequest =myHttpRequest
        self.cardtheme = cardtheme
        self.thread_stop = False
   
    def run(self):
        self.window.database.cu.execute("select * from cardtheme where type=?",(0,))
        result =self.window.database.cu.fetchall()
        for themeItem in result:
            base_url = commons.getUrl(constant.THEMELISTURL,self.myHttpRequest)
            postData = {
                   'uin':constant.USERNAME,
                   'tid':int(themeItem[1])
            }
            try:
                result = self.myHttpRequest.get_response(base_url,postData).read()
                #print result
                soup = BeautifulSoup(result)
                userList = []
                nodeList = soup.find_all('node')
                for nodeItem in nodeList:
                    soup = BeautifulSoup(str(nodeItem))
                    uinlist = soup.node['uin']
                    uinList = uinlist.split('|')
                    for uin in uinList:
                        userList.append(uin)
                    for user in userList:
                        print 'search user',user
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
                            if self.window.database.getCardThemeid(pid)==self.cardtheme:
                                wx.CallAfter(self.window.updateLog,user)
                                file = open('1.txt','a')
                                file.write(str(user)+'\n')
                                file.close()
                                break

                        time.sleep(0.5)
            except Exception:
                continue
        
    def stop(self):
        self.thread_stop = True

        