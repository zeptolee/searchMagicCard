# -*- coding: utf-8 -*-
from commonlib import myhttp
from commonlib import constant
from commonlib import Tea
import  re,wx,urllib2
import mythread.myThread as myThread
import thread
import main,time
import commonlib.carddatabase as carddatabase
import os,sys,md5
import StringIO
class MyLogin(wx.Frame):
    
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(750,150))
        self.cap_cd = ''
        self.isNeedCodePattern = re.compile(ur"\((.*?)\)")
        self.isNeedCode =0
        self.loginCode = ''
        self.myHttpRequest = myhttp.MyHttpRequest()
        
        #if not  os.path.exists(constant.DATABASE):
        thread.start_new_thread(self.readFile,(1,))
        
        

        #-------------用户信息----------
        self.userInfoSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.tidLabel = wx.StaticText(self,-1,u'用户名')#-1的意义为id由系统分配
        self.tidInput = wx.TextCtrl(self,-1)
        self.tidInput.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
        self.tidInput.Bind(wx.EVT_SET_FOCUS,self.OnSetFocus)
        self.aidLabel = wx.StaticText(self,-1,u'密码')
        self.aidInput = wx.TextCtrl(self,-1,style=wx.TE_PASSWORD)
        self.codeImage=wx.StaticBitmap(self, -1,  pos=(30,50), size=(150,80))
        self.codeLabel = wx.StaticText(self,-1,u'验证码')#-1的意义为id由系统分配
        self.codeInput = wx.TextCtrl(self,-1)
        self.codeLabel.Show(False)
        self.codeInput.Show(False)
        self.codeImage.Show(False)
        self.loginButton = wx.Button(self,-1,u'登陆')
        self.Bind(wx.EVT_BUTTON, self.loginQQ, self.loginButton)
        
        self.userInfoSizer.Add(self.tidLabel,0,wx.ALL,10)
        self.userInfoSizer.Add(self.tidInput,0,wx.ALL,10)
        self.userInfoSizer.Add(self.aidLabel,0,wx.ALL,10)
        self.userInfoSizer.Add(self.aidInput,0,wx.ALL,10)
        self.userInfoSizer.Add(self.codeImage,0,wx.TOP,10)
        self.userInfoSizer.Add(self.codeLabel,0,wx.TOP,10)
        self.userInfoSizer.Add(self.codeInput,0,wx.ALL,10)
        self.userInfoSizer.Add(self.loginButton,0,wx.ALL,10)
        
        #---------------总体布局----------
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.userInfoSizer, 0, wx.EXPAND)
        #Layout sizers
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        '''显示在屏幕中间
        '''
        self.Center()
        self.Show(True)
    def OnKillFocus(self,e):
        constant.USERNAME = int(self.tidInput.GetValue())
        thread = myThread.GetCodePicThread(self,self.myHttpRequest,constant.USERNAME)
        thread.start()
        
    def OnSetFocus(self,e):
        pass
    
    
    
    #显示验证码 图片
    def showTheCodePic(self,msg):
        if(msg==0):
            self.codeImage.Show(False)
            self.codeLabel.Show(False)
            self.codeInput.Show(False)
            self.sizer.Layout()
        else:
            self.codeImage.Show(True)
            self.codeLabel.Show(True)
            self.codeInput.Show(True)
            self.sizer.Layout()
            Image = wx.ImageFromStream(StringIO.StringIO(msg)).ConvertToBitmap()   
            self.codeImage.SetBitmap(Image) 
        
       
    def loginQQ(self,e):
        
        
        try:
            configFile = open('Mfkp_config.ini','r')
            mystr = configFile.readline()
            if  str(constant.USERNAME) in mystr:
                constant.COLLECTTHEMEID = int(configFile.readline().split('=')[1])
                constant.STEALFRIEND = int(configFile.readline().split('=')[1])
                constant.QQSHOWSELECT = int(configFile.readline().split('=')[1])
                constant.QQSHOWID = int(configFile.readline().split('=')[1])
                configFile.close()
        except Exception:
            print 'file can not find'
        
        verifysession = ''
        if self.codeInput.IsShown():
            code = str(self.codeInput.GetValue())
            
            for ck in self.myHttpRequest.cj:
                if ck.name=='verifysession':
                    verifysession = ck.value
        else:
            code = str(constant.CODE)
            verifysession = str(constant.SESSION)
        constant.PASSWORD = str(self.aidInput.GetValue())
        password = Tea.getTEAPass(constant.USERNAME,constant.PASSWORD,code)
        base_url = constant.LOGINURL
        base_url = base_url.replace('USERNAME', str(constant.USERNAME))
        base_url = base_url.replace('VERIFYSESSION', verifysession)
        base_url = base_url.replace('PASSWORD',password)
        base_url = base_url.replace('CODE',code)
        page_content = self.myHttpRequest.get_response(base_url)
        result =  page_content.read()
        if  str(constant.USERNAME) in result:
            dlg = wx.MessageDialog(self,u"密码或验证码不正确",caption=u'提示',style=wx.OK,pos=wx.DefaultPosition)
            retCode = dlg.ShowModal()
            if retCode == wx.ID_OK:
                dlg.Destroy()
        else:
            self.Destroy()
            main.Main(None,u'魔法卡片',self.myHttpRequest,self.database)
        
        
    #登陆魔卡
    def loginCard(self):
        skey = ''
        for ck in self.myHttpRequest.cj:
                if ck.name=='skey':
                    skey = ck.value
        postData = {
                        'code':'',
                        'uin':constant.USERNAME
                
        }            
        base_url = constant.CARDLOGINURL
        base_url = base_url.replace('GTK', str(Tea.getGTK(skey)))
        page_content = self.myHttpRequest.get_response(base_url,postData)
        return   page_content.read()



    #读取数据库信息
    def readFile(self,num):
        response = urllib2.urlopen('http://appimg2.qq.com/card/mk/card_info_v3.xml').read()
        if os.path.exists('card_info_v3.db'):
            dbFileTemp = open('card_info_v3_temp.db','w')
            dbFileTemp.write(response)
            dbFileTemp.close()
            fileTemp = open('card_info_v3_temp.db','r')
            fileDB  = open('card_info_v3.db','r')
            if md5.new(fileTemp.read()).digest()!=md5.new(fileDB.read()).digest():
                fileDB.close()
                fileTemp.close()
                os.remove('card_info_v3.db')
                os.rename('card_info_v3_temp.db', 'card_info_v3.db')
                os.remove('test.db')
            else:
                fileTemp.close()
                os.remove('card_info_v3_temp.db')
        else:
            dbFileTemp = open('card_info_v3.db','w')
            dbFileTemp.write(response)
            dbFileTemp.close()
        self.database = carddatabase.CardDataBase(self.cur_file_dir())


    #获取脚本文件的当前路径
    def cur_file_dir(self):
        #获取脚本路径
        path = sys.path[0]
        #判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，如果是py2exe编译后的文件，则返回的是编译后的文件路径
        if os.path.isdir(path):
            return path+"\\"
        elif os.path.isfile(path):
            return os.path.dirname(path)+"\\"   
    
    #获取对应的url  
    def getUrl(self,url):
        skey = ''
        for ck in self.myHttpRequest.cj:
                if ck.name=='skey':
                    skey = ck.value
        base_url = url
        base_url = base_url.replace('GTK', str(Tea.getGTK(skey)))
        return base_url
                
app = wx.App(False)
frame = MyLogin(None, u"qq登陆器")
app.MainLoop()



