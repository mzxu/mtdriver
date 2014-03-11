'''
Created on Jul 5, 2012

@author: szheng
'''

"""
The MTdriver implementation.
"""

import httplib, json, base64, datetime, time, socket

from PIL import Image, ImageDraw
import paramiko
import os, sys
from ChorusCore import Utils
from subprocess import Popen
import shlex
#defines the UITable's size with up-left corner's and down-right conner's coordinates default using alert's ios simulator frame size 
UITableViewRange = [0, 64, 320, 431]
class DefaultThinkTime:
    long	= 1000
    medium	= 500
    small	= 300
    
class DefaultTimeOut:
    long	= 4000
    medium	= 2000
    small	= 1000

class Component:
    button  = "b"
    input   = "i"
    view    = "v"
    label   = "l"
    table   = "t"
    cell    = "c"
    image   = "im"
    scroll  = "s"
    ctcLabel= "cl"
    ctcView = "cv"  
    TextView= 'tv'
    TextArea = 'ta'

class MTDriver(object):
    """
    Controls a mobile device by sending commands to the MonkeyTalk agent server.
   
    """
#    private static final SimpleDateFormat dateFmt = new SimpleDateFormat("yyyy-MM-dd_HHmmss");
#    private static final String SCREENSHOTS_DIR = "screenshots";
    
    def __init__(self, host):
        """
        init work include:
        1.set device by given ip,
        2.ios compile info
        3.lauch app on specific device
        @param host: ip address and port number related to a device, example: 10.197.115.18:16863
        """
        self.host=host
        self.thinktime = 500
        self.timeout = 2000
        self.sleep = 0
        self.counter = 0 #number of failed actions
        self.device = self.host.split(':')[0]
        self.port = self.host.split(":")[1]
        if self.port == "16863":
            self.type = 'iOS'
        else:
            self.type = 'Android'
            
        self.crashFlag = False
        self.inittime = int(time.time())
        if self.type == 'iOS':
            self.appName = "Alert.app"
            self.appIdentifier = "com.strategy.alert"
            self.target = self.appName.split(".")[0]
            self.sshRoot = "root"
            self.sshMobile = "mobile"
            self.sshRootPasswd = "alpine"
            self.sshMobilePasswd = "alpine"    
            self.dsymPath = "/Users/gaojian/Workspace/build-out/Release-iphoneos/Alert.app.dSYM"
            '''if you want to use MTDriver on none jail break devices comment the following lines'''
            '''
            self.launchApp(self.appIdentifier, self.appName)
            self.pid = self.getPid()
            
            print "test connection..."
            
            try:
                self.testConnection()
                print "connection test pass"
                    
            except Exception, e:
                raise ConnectError("cannot establish connection with %s" %self.device)
            
        else:
            self.pid = None
            pass
            '''
        '''
        False => Crash
        True => No Crash
        '''
        
    #===========================================================================
    # 
    #===========================================================================
    def testConnection(self):
        """
        test if Connection has established with the device
        @return: true if connection is ok. else return false 
        """
        try:
            self.execute("p__",  "Tap", "Button", thinktime=0, timeout=0)
            return True
        except Exception, e:
            raise 
            return False
    
    
    
    def getPid(self):
        """
        get the pid belongs to app 
        @return: pid, return None if to pid was found match the app
        """
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.device, username=self.sshRoot, password=self.sshRootPasswd)
        if self.port =="16863" :
            cmd ="ps -e |grep -v '\<grep\>' |grep /var/mobile/Applications/*/%s |awk  '{print $1}'" %self.appName
            stdin, stdout, stderr = ssh.exec_command(cmd)
            res = stdout.readlines()
        else:
            cmd ="andrid device cmd"
            res = [] 
        
        if res == []:
            pid = None
        else:
            pid = res[0].split("\n")[0]
        ssh.close()
        return pid
    
    def setThinkTime(self, thinktime):
        self.thinktime = thinktime
        
    def setTimeOut(self, timeout):
        self.timeout = timeout

    def setAppName(self, appName):
        self.appName = appName
    
    def setSleepTime(self, delay):
        '''
        global sleep
        You can specify the sleep time before executing a command. This is used for bad network condition
        '''
        print "Global sleep time is set to %s" % str(delay)
        self.sleep = delay
        
    def counterReset(self):
        self.counter = 1
    
    def counterAdd(self):
        self.counter += 1
        print "Number of failed actions: %i" % self.counter
        
    def counterGet(self):
        return self.counter
        
    '''
    start:
    launch app
    '''
    def launchApp(self,appidentifier,appname):
        """
        launch the app on this device
        
        @param appidentifier: identifier of an app. example: com.strategy.alert
                                
                                application name for Android. e.g. com.alert.uat 
                                
        @type appidentifier: str
        @param appname: process name of an app. example: Alert.app
        
                                Launching activity name. e.g. com.alert.ui.activity.DispatchActivity
        @type appname: str
        """
        print self.device   
        if self.type == "iOS":    
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(self.device, username=self.sshRoot, password=self.sshRootPasswd)
                cmd = "open %(appidentifier)s" %{'appidentifier': appidentifier}
                stdin, stdout, stderr = ssh.exec_command(cmd)
                print "App is launching... plz wait"
                ssh.close()
            except Exception, e:
                raise SSHError('cannot ssh to device!')
                    
            inittime = int(time.time())
            while self.isProcessAlive(appname) == False:
                print "... ..."
                time.sleep(1)
                if int(time.time())-inittime > 10:
                    print "failed to launch app"
                    break
        else:   #Android
            try:
                dev = self.device + ":5555"
                cmd = "adb connect " + dev
                #print cmd
                print os.system(cmd)
                cmd = "adb -s " + dev + " shell am start -a android.intent.action.MAIN -n " + appidentifier +'/' + appname
                print cmd 
                print os.system(cmd)
                print "App is launching... plz wait"
            except Exception, e:
                raise 'cannot connect device'
                
        
    
    def isProcessAlive(self, processName):
        """
        check if process is alive, apart of launch and close app
        Will raise SSHError if cannot access through SSH
        
        @param processName: process name of an app. example: Alert.app
        @type processName: str
        
        @return: True if process is alive, else it return False
        """
        device = self.device
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(device, username='root', password='alpine')
            cmd = " ps -e |grep -v '\<grep\>' |grep /var/mobile/Applications/*/%(appname)s" %{'appname':processName}
            stdin, stdout, stderr = ssh.exec_command(cmd)
            res = stdout.readlines()
            ssh.close()    
            if res == []:
                return False
            else:
                return True
        except Exception, e:
            raise SSHError('cannot ssh to device!')
            
    def isAppCrash(self):
        """
        check if app Crash, 
        mechanism: check the latestCrash log, see if the pid in the log matches with slef.pid, the one belong to an app
        
        @return: True if Crash happened
        """
        latestCrashLog = "/var/mobile/Library/Logs/CrashReporter/LatestCrash.plist"
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.device, username='root', password='alpine')
            cmd = "ls -l %(filename)s | awk -F \"-> \" '{print $2}'" %{'filename': latestCrashLog}
            stdin, stdout, stderr = ssh.exec_command(cmd)
            logfile =  "/var/mobile/Library/Logs/CrashReporter/"+stdout.readlines()[0].split("\n")[0]
            cmd = "grep \\^Process %s |awk '{print $3}' |awk -F \"[\" '{print $2}' |awk -F \"]\" '{print $1}' " %logfile
            #cmd = "stat %(logfile)s |grep Birth |awk -F \" \" '{print $2, $3}' |awk -F \".\" '{print $1}' " %{'logfile': logfile}
            stdin, stdout, stderr = ssh.exec_command(cmd)
            pid=stdout.readlines()[0].split("\n")[0]
            print pid
            if self.pid == pid:
                return True
            else:
                return False
            ssh.close()
        except Exception, e:
            raise SSHError('cannot ssh to device!')
        #logCreateTime=stdout.readlines()[0].split("\n")[0]
        
        #cmd = "date -d \""+logCreateTime+"\" +%s"
        #stdin, stdout, stderr = ssh.exec_command(cmd)
        #logCreateTime=stdout.readlines()[0].split("\n")[0]
        #print int(logCreateTime)
        #print self.inittime
        
        #ssh.close()
        #if int(logCreateTime)>self.inittime:
        #    return True
        #else:
        #    return False
            
    def closeApp(self,appname):
        """
        close the app, usually this is called when all tests are executed
        
        @param appname: process name of an app 
        """
        device = self.device
        if self.type == 'iOS':
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(device, username='root', password='alpine')
                cmd = " ps -e |grep -v '\<grep\>' |grep /var/mobile/Applications/*/%(appname)s | awk '{print $1}' |xargs kill -9" %{'appname':appname}
                stdin, stdout, stderr = ssh.exec_command(cmd)
                #print stdout.readlines()
                if self.isProcessAlive(appname) == False:
                    print "%(appname)s has been closed." %{'appname':appname} 
                else:
                    print "close %(appname)s failed" %{'appname':appname}
                
                ssh.close()
            except Exception, e:
                raise SSHError('cannot ssh to device!')
            
        else: #Android
            try:
                dev = self.device + ":5555"
                cmd = "adb connect " + dev
                #print cmd
                print os.system(cmd)
                cmd = "adb -s " + dev + " shell am force-stop " + appname
                #print cmd 
                print os.system(cmd)
                print "app closed"
            except Exception, e:
                raise 'cannot connect device'
            
    #===========================================================================
    # execute functions. 
    #===========================================================================
    def post(self, host, header, body):
        """
        general methold of sending POST to the host(device)
        
        @param host: device's ip address
        @type host: str
        
        @param header: header of this POST  
        @type header: str
        
        @param body: body of this POST
        @type body: str
        """
        try:
            #request timeout is set to 6 minutes
            conn = httplib.HTTPConnection(host, timeout=30)
            data = json.dumps(body)
            conn.request("POST", "/fonemonkey", data, header)
            response = conn.getresponse()
            if response.reason!='OK':
                print "resp error. status: %s, reason: %s" % (response.status, response.reason)
            #print "resp info: %s, %s" % (response.status, response.reason)
            data = response.read()
            #print "resp data: %s" % data
            return data
        except socket.timeout, e:
            print "Host: %s" % host
            print "Post data: %s" % data
            print "Header: %s" % header
            raise TimeoutError("Request timeout!")
        except socket.error, e: 
            print "Connection cannot be made, please make sure mobile's ip address and port is correct!!!"
            '''
            answer = raw_input("Do you want to restart this program ? ")
            if answer.strip() in "y Y yes Yes YES".split():
                restart_program()
            '''
            if self.isAppCrash():
                raise CrashError('opps, app crashed, please see the log')
            raise ConnectError("Connection cannot be made, please make sure mobile's ip address and port is correct!!!")
            #self.crashFlag = self.isProcessAlive(self.appName)
        finally:
            conn.close()
    def componentType(self, component):
        """
        return the actual type of component for iOS or Android    
        """
    
        if component == "*" or len(component)>3:
            return component
        
        ios_type    = { "i" : "UITextField"     ,\
                        "v" : "UIView"          ,\
                        "b" : "UIButton"        ,\
                        "t" : "UITableView"     ,\
                        "c" : "UITableViewCell" ,\
                        "im": "MIImageView"     ,\
                        "l" : "UILabel"         ,\
                        "cl": "UILabel"         ,\
                        "tv": "UITextView"      ,\
                        "ta": "UITextArea"      ,\
                        "s" : "UIScrollView"}
        android_type= { "i" : "Input"           ,\
                        "b" : "Button"          ,\
                        "t" : "Table"           ,\
                        "v" : "View"            ,\
                        "cv": "CTCView"         ,\
                        "cl": "CTCLabel"        ,\
                        "l" : "Label"           ,\
                        'ta': 'TextArea'}
        
        if self.type == "iOS" and ios_type.has_key(component):      
            return ios_type[component]
        if self.type == "Android" and android_type.has_key(component):
            return android_type[component]
        
        return component
            
    def execute(self, monkeyId, action, component, args=None, thinktime=None, timeout=None, mtcommand = None, midProperty = None, isResetCounter = True, isCounted = True):
        """
        execute monkey talk command        
        """
        time.sleep(self.sleep)
        component = self.componentType(component)
        if mtcommand:
            mtcmd = mtcommand
        else:
            mtcmd = "PLAY"
            
        if thinktime == None:
            thinktime = self.thinktime
        if timeout == None:
            timeout = self.timeout
        if args is None:
            body={"timestamp"   :1340072129698     ,\
                  "mtcommand"   :mtcmd            ,\
                  "monkeyId"    :monkeyId          ,\
                  "args"        :[]                ,\
                  "mtversion"   :1                 ,\
                  "action"      :action            ,\
                  "modifiers":{"thinktime":thinktime,"timeout":timeout,"screenshotonerror":"false"},\
                  "componentType":component}
        else:
            if not isinstance(args, list):
                args = [args]
            body={"timestamp"   :1340072129698    ,\
                  "mtcommand"   :mtcmd           ,\
                  "monkeyId"    :monkeyId         ,\
                  "mtversion"   :1                ,\
                  "args"        :args             ,\
                  "action"      :action           ,\
                  "modifiers":{"thinktime":thinktime,"timeout":timeout,"screenshotonerror":"false"},\
                  "componentType":component}
        #if mid property is not none, add it to the request body
        if midProperty:
            body['midProperty'] = midProperty
            
        header={'Content-Type':'application/json','User-Agent':'Java/1.6.0_31','Connection':'keep-alive','Host':self.host,'Accept':'text/html, image/gif, image/jpeg, *; q=.2, */*; q=.2','Content_Length':'199'}
        print '[ ', action, monkeyId, component, args, ' ]'  
        sys.stdout.flush()
        
        try:
            response = self.post(self.host, header, body)
            
            respDict = json.loads(response)
            if respDict['result']=='FAILURE':
                if isCounted:
                    self.counterAdd()
                print respDict['message'].encode("utf-8")
                if self.counterGet() >= 10:
                    self.counterReset()
                    raise TooManyFailedActionsError("Too many failed actions. Please fail the test!")
            else:
                if isResetCounter:
                    self.counterReset()
            return response
        except CrashError:
            raise
        except TooManyFailedActionsError:
            self.counterReset()
            raise
        except SSHError:
            if isCounted:
                self.counterAdd()      
            if self.counterGet() >= 10:
                self.counterReset()
                raise TooManyFailedActionsError("Too many failed actions. Please fail the test!")
            return False      
        except Exception, e:
            print e
            return False
      
    #===========================================================================
    # Screenshot
    #===========================================================================
    """
    :Usage:
            driver.get_screenshot_as_file('/Screenshots/foo.png')
    """
    def get_screenshot_as_file(self, filename, component="Device", monkeyId="*"):
        if component == "Device":
            monkeyId = "*"
        try:
            if self.type == 'iOS':
                responsedata=self.execute(monkeyId, "Screenshot", component, isResetCounter = False)
            else:
                responsedata=self.execute(monkeyId, "ctcScreenshot", component, isResetCounter = False)
#            print responsedata
            dic=json.loads(responsedata)

            screenshot=dic.get("message").get("screenshot")
            
            imgData=base64.b64decode(screenshot)
#        filename=datetime.datetime.now().strftime('%Y%m%d%H%M%S')+".png"

            imgFile=open(filename, 'wb')
            imgFile.write(imgData)
            print('capture screenshot done')
            return True
        except  CrashError:
            raise
        except TooManyFailedActionsError:
            raise
        except  Exception, e:
            print ('capture screenshot error')
            print type(e)
            print e
            return False
    
    def get_screenshot_as_file_with_cordinates(self,filename,componentType,monkeyID):
        print "get screenshot with centain cordinates of selected elements"
        self.get_screenshot_as_file(filename)
        cordist=self.GetItemLocation(monkeyID, componentType)
        self.transformRec(filename, cordist)
    
    #code review: duplicate code
    def get_screenshot_as_file_without_topbar(self, filename):
        self.get_screenshot_as_file(filename, isResetCounter = False)
        try:
            pre = Image.open(filename)
        except Exception, e:
            print ("file open error")
        bd = pre.getbbox()
        
        aft = pre.crop(((bd[0],bd[1]+40,bd[2],bd[3])))
        try:
            aft.save(filename)
        except TooManyFailedActionsError:
            raise
        except Exception, e:
            print ('remove top bar image process error')
            print type(e)
            print e
            return False

 
    def get_screenshot_as_base64(self):
        try:
            responsedata=self.execute("*", "Screenshot", "Device", isResetCounter = False)
            dic=json.loads(responsedata)
            screenshot=dic.get("message").get("screenshot")
            return screenshot
        except  CrashError:
            raise
        except TooManyFailedActionsError:
            raise
        except  Exception, e:
            print e
            return False
        
    #===========================================================================
    # Get Screenshot with Mark, related functions
    #===========================================================================

    #code review: _ private method
    def GetItemLocation(self, monkeyId, componentType, args=None):
        '''
        return frame (x, y, width, height)
        '''
        data = self.DumpViewData(componentType,monkeyId,  args)
        try:
            if self.type == 'iOS':
    
                    dic = json.loads(data)
            else:
                dic = data
            
            x = int(dic['frame']['x'])
            y = int(dic['frame']['y'])
            height = int(dic['frame']['height'])
            width = int(dic['frame']['width'])
            return [x, y, x+width, y+height]
        except:
            print "no element found with monkeyid:%s and componenttype:%s" % (monkeyId, componentType)
            return {}
    
    def drawRec(self,filename, cordlist, color=(0,0,0)):
        '''
        draw rectangles to images
        '''
        im = Image.open(filename)
        reslutionlist = im.getbbox()
        #solve the device reslution problem
        width = reslutionlist[2]
        #simulator's reslution width is 320
        if self.type == 'iOS':
            ratio = width/320
        else:
            ratio = 1
        draw = ImageDraw.Draw(im)
        for cord in cordlist:
            newcord = (cord[0]*ratio, cord[1]*ratio, cord[2]*ratio, cord[3]*ratio)
            draw.rectangle(newcord, fill=color)
            #im.show()
        del draw
        newfile = filename
        im.save(newfile)
        return newfile
    
    def transformRec(self,filename,cordist):
        '''
        cut a rectangle from a picture
        '''
        im = Image.open(filename)
        size = (cordist[2]-cordist[0],cordist[3]-cordist[1])
        newcord = (cordist[0],cordist[1],cordist[2],cordist[3])
        im.transform(size,Image.EXTENT,newcord)
        newfile=filename
        im.save(newfile)
        return newfile
        
    def getScreenshotWithoutElement(self, filename, componentList, monkeyIdList, arglist):
        self.get_screenshot_as_file(filename)
        cordlist = []
        for item in map(lambda x,y,z:(x,y,z), componentList, monkeyIdList, arglist):
            cordlist.append(self.GetItemLocation(item[1], item[0], item[2]))
        new = self.drawRec(filename, cordlist)
        
    def get_screenshot_without_items(self, filename, items,cordinates = None):
        print "get screenshot without centain items"
        self.get_screenshot_as_file(filename)
        cords = []
        if items:
            for item in items:
                cord = self.GetItemLocation(item[1], item[0])
                if cord:
                    cords.append(cord)
        if cordinates:
            for cord in cordinates:
                cords.append(cord)
        self.drawRec(filename, cords)
            
    
    def getElementFrame(self, dic, flag):
        '''return element's coordinate'''
        x = int(dic['frame']['x'])
        y = int(dic['frame']['y'])
        height = int(dic['frame']['height'])
        width = int(dic['frame']['width'])
        
        global UITableViewRange 
        if  y+height<UITableViewRange[1]:
            #if head icon just return 
            print (x, y, x+width, y+height)
            return (x, y, x+width, y+height)
        if flag == True: #UITableView exists
            x_up = x<UITableViewRange[0] and UITableViewRange[0] or x
            y_up = y<UITableViewRange[1] and UITableViewRange[1] or y
            x_down = x+width<UITableViewRange[2] and x+width or UITableViewRange[2]
            y_down = y+height<UITableViewRange[3] and y+height or UITableViewRange[3] 
            return (x_up, y_up, x_down, y_down)
        else:
            y_up = y<UITableViewRange[1] and UITableViewRange[1] or y
            return (x, y_up, x+width, y+height)
    
        
        
    def getImageFrame(self, dic, imageCoordinateList, flag):
        '''return image's coordinate'''
        if self.type == 'iOS':
            if dic['component'] == 'MIImageView':
                imageCoordinateList.append(self.getElementFrame(dic, flag))
            if dic['children'] != []:
                for child in dic['children']:
                    tem = self.getImageFrame(child, imageCoordinateList, flag)
                    if tem == imageCoordinateList:
                        pass
                    else:
                        imageCoordinateList = tem
                        #imageCoordinateList.append(tem) 
            else:
                pass
        else:
            if dic['value'].has_key('imageURL'):
                imageCoordinateList.append(self.getElementFrame(dic, flag))
            if dic['children'] != []:
                for child in dic['children']:
                    tem = self.getImageFrame(child, imageCoordinateList, flag)
                    if tem == imageCoordinateList:
                        pass
                    else:
                        imageCoordinateList = tem
                        #imageCoordinateList.append(tem) 
            else:
                pass
            
        return imageCoordinateList
            
    def getScreenshotWithMarkup(self, filename):
        '''get screen shot and auto add black mark to it'''
        if self.type == 'iOS':
            viewData = self.DumpViewData('UILayoutContainerView','#1',  ['urlPath'])
            d = json.loads(viewData)
            res = self.execute('*', 'FindElement', 'UITableView')
            if json.loads( res)['result'] == 'OK':
                flag = True
                global UITableViewRange
                UITableViewRange = self.GetItemLocation('*', 'UITableView')
                print UITableViewRange
            else:
                flag = False
            coordlist = self.getImageFrame(d, [], flag)
        else:
            viewData = self.DumpViewData('Table','*',  ['imageURL'])
            global UITableViewRange
            UITableViewRange = self.GetItemLocation('*', 'Table')
            print UITableViewRange
            coordlist = self.getImageFrame(viewData, [], True)
        
        print 'cordlist:' 
        print coordlist    
        self.get_screenshot_as_file(filename)
        self.drawRec(filename, coordlist)   
        
    