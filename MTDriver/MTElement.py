'''
Created on Sep 27, 2012

@author: mxu
'''
class MTComponentType:
    '''
    IOS components:
        UIButton
        UITextView
                
    Web components:
        Button
        Input
    '''
    default = "Button"
    Button = "Button" 
    Scroller = "Scroller"
    UIButton = "UIButton"
    UIDatePicker = "UIDatePicker"
    UIToolbarButton = "UIToolbarButton"
    UILabel = "UILabel"
    UITextView = "UITextView"
    UITextField = "UITextField"
    UITableViewCell = "UITableViewCell"
    UITableViewCellEditControl = "UITableViewCellEditControl"
    UITableViewCellRecorderControl = "UITableViewCellRecorderControl"
    UIKeyboardLayoutStar = "UIKeyboardLayoutStar"
    _UITableViewCellDeleteConfirmationControl = "_UITableViewCellDeleteConfirmationControl"
    CCGLView = "CCGLView"
    UIView = "UIView"
    UISwitch = "UISwitch"
    _UIWebViewScrollView = "_UIWebViewScrollView"
    FBLoginDialog = "FBLoginDialog"
    Input = "Input"
    Image = "Image"
    UITableView = "UITableView"
    UISwitch = "UISwitch"
    Device = "Device"
    QRCodeMethodView="QRCodeMethodView"
    UIWindow="UIWindow"
    Extend = "Extend"
    
class MTProperty:
    accessibilityLabel = "accessibilityLabel"
        
class MTElement:
    def __init__(self, Object = None, ComponentType = None, MonkeyID = None, Args = None, midProperty = None):
        if not ComponentType:
            raise MTException.NoComponentTypeError
        
#        if not MonkeyID:
#            raise MTException.NoMonkeyIDError
                
        #Object can be mtdriver instance itself or an object with mtdriver instance attribute
        if hasattr(Object, "mtdriver"):
            self.mtdriver = Object.mtdriver
        elif Object:
            self.mtdriver = Object
        else:
            raise MTException.NoMTDriverInstanceError
                    
        self.ComponentType = ComponentType 
        self.MonkeyID= MonkeyID
        self.Args = Args
        self.midProperty = midProperty
        
        
    def Tap(self, *args):
        self.mtdriver.execute(self.MonkeyID, "Tap", self.ComponentType, self.Args, midProperty = self.midProperty)

    
    def TapByPoint(self, *args):
        self.mtdriver.execute("", "TapByPoint", MTComponentType.Device, self.Args, midProperty = self.midProperty)
        
    
    def EnterText(self, value):
        self.Args = value
        self.mtdriver.execute(self.MonkeyID, "EnterText", self.ComponentType, self.Args, midProperty = self.midProperty)

 
    def Delete(self, *args):
        self.mtdriver.execute(self.MonkeyID, "Delete", MTComponentType.UITableView, self.Args, midProperty = self.midProperty)
        
    def ActivateEditor(self, *args):
        self.mtdriver.execute(self.MonkeyID, "ActivateEditor", self.ComponentType, self.Args, midProperty = self.midProperty)

    def SwitchOn(self, *args):
        self.mtdriver.execute(self.MonkeyID, "On", self.ComponentType, self.Args, midProperty = self.midProperty)
        
    def SwitchOff(self, *args):
        self.mtdriver.execute(self.MonkeyID, "Off", self.ComponentType, self.Args, midProperty = self.midProperty)

    def Scroll(self, *args):
        self.mtdriver.execute(self.MonkeyID, "Scroll", self.ComponentType, self.Args, midProperty = self.midProperty)
        
    def ScrollToRow(self, *args):
        self.mtdriver.execute(self.MonkeyID, "ScrollToRow", MTComponentType.UITableView, self.Args, midProperty = self.midProperty)
            
    def Swipe(self, *args):
        self.mtdriver.execute(self.MonkeyID, "Swipe", self.ComponentType, self.Args, midProperty = self.midProperty)
    
    def SetCheckIndicator(self,*args):
        self.mtdriver.execute(self.MonkeyID, "setCheckIndicator",self.ComponentType,self.Args,midProperty = self.midProperty)
    
    def TouchDown(self,*args):
        self.mtdriver.execute(self.MonkeyID, "TouchDown",self.ComponentType,self.Args,midProperty = self.midProperty)

    def MoveMacro(self,*args):
        self.mtdriver.execute(self.MonkeyID, "MoveMacro",self.ComponentType,self.Args,midProperty = self.midProperty)

    def TouchUp(self,*args):
        self.mtdriver.execute(self.MonkeyID, "TouchUp",self.ComponentType,self.Args,midProperty = self.midProperty)
    
    def OpenLink(self,*args):
        self.mtdriver.execute(self.MonkeyID, "OpenLink",MTComponentType.Device,self.Args,midProperty = self.midProperty)

    def DoubleTap(self,*args):
        self.mtdriver.execute(self.MonkeyID, "DoubleTap",self.ComponentType,self.Args,midProperty = self.midProperty)
    
    def Verify(self, *args, **kwargs):
        try:
            if kwargs.has_key('isCounted'):
                isCounted = kwargs['isCounted']
                print "skip counter for wait for"
            else:
                isCounted = True
            responsedata = self.mtdriver.execute(self.MonkeyID, "Verify", self.ComponentType , midProperty = self.midProperty, isCounted = isCounted ) 
                #webview cannot find element, so change to use verify command
                #responsedata=self.execute(monkeyId, "Verify", componentType, None)
            dic=json.loads(responsedata)         
            if dic["result"]== "OK":
                return True
            else:
                return False
        except  MTException.CrashError:
            raise
        except TooManyFailedActionsError:
            raise
        except  Exception, e:
            #print e
            return False
        
    def VerifyTappable(self, *args, **kwargs):
        try:
            if kwargs.has_key('isCounted'):
                isCounted = kwargs['isCounted']
                print "skip counter for wait for tappable"
            else:
                isCounted = True
                
            responsedata = self.mtdriver.execute(self.MonkeyID, "Verify", self.ComponentType, self.Args, midProperty = self.midProperty, isCounted = isCounted) 
                 
            dic=json.loads(responsedata)           
            if dic["result"]=='OK':
                canBeTaped = json.loads(dic['message'])
                if canBeTaped['canBeTaped'] == "YES":
                    return True
                else:
                    print "Component is hidden in this view"
                    return False
            else:
                return False
        except  MTException.CrashError:
            raise
        except TooManyFailedActionsError:
            raise        
        except  Exception, e:
            print e
            return False
        
    def WaitFor(self, timeout=30,timedelay=True, *args):
        isExist = self.Verify(self.MonkeyID, self.ComponentType, isCounted = False)  #to prevent loading, make time record after the first get
        #print "timeout="+str(timeout)
        inittime = int(time.time())
        while (not isExist):
            #print "not rendered yet"
            isExist = self.Verify(self.MonkeyID, self.ComponentType, isCounted = False)  
            if (int(time.time())-inittime>timeout):
                print "Component Time Out"
                return False
            if timedelay: 
                time.sleep(1)
        return True
        
    def WaitForTappable(self,timeout=30,timedelay=True, *args):
        isTappable = self.VerifyTappable(self.MonkeyID, self.ComponentType, isCounted = False)  #to prevent loading, make time record after the first get
        #print "timeout="+str(timeout)
        inittime = int(time.time())
        while (not isTappable):
            #print "not rendered yet"
            isTappable = self.VerifyTappable(self.MonkeyID, self.ComponentType, isCounted = False)  
            if (int(time.time())-inittime>timeout):
                print "Component Time Out"
                return False
            if timedelay: 
                time.sleep(1)
        return True
    def WaitForNotTappable(self,timeout=30, *args):
        isTappable = self.VerifyTappable(self.MonkeyID, self.ComponentType, isCounted = False)  #to prevent loading, make time record after the first get
        #print "timeout="+str(timeout)
        inittime = int(time.time())
        while (isTappable):
            #print "not rendered yet"
            isTappable = self.VerifyTappable(self.MonkeyID, self.ComponentType, isCounted = False)  
            if (int(time.time())-inittime>timeout):
                print "Component Time Out"
                return False
            time.sleep(1)
        return True
    def WaitForDisappear(self,timeout=30,timedelay=True, *args):
        isExist = self.Verify(self.MonkeyID, self.ComponentType, isCounted = False)  #to prevent loading, make time record after the first get
        #print "timeout="+str(timeout)
        inittime = int(time.time())
        while (isExist):
            #print "not rendered yet"
            isExist = self.Verify(self.MonkeyID, self.ComponentType, isCounted = False)  
            if (int(time.time())-inittime>timeout):
                print "Compoent not disappeared until timeout"
                return False
            if timedelay: 
                time.sleep(1)
        print "Component disappeared successful"
        return True
            
    def LongPress(self):
        self.mtdriver.execute(self.MonkeyID, "TouchLong", self.ComponentType)
        
    def Drag(self):
        '''
        args should like this: "{x1,y1};{x2,y2};{x3,y3}..."
        '''
        self.mtdriver.execute(self.MonkeyID, "Drag", self.ComponentType, self.Args)
    
    def Move(self):
        '''
        only for UITableView
        '''
        self.mtdriver.execute("*", "Move", MTComponentType.UITableView, self.Args)
        
    def Select(self):
        '''
        select a row in a table view by monkey id
        '''
        self.mtdriver.execute(self.MonkeyID, "Select", MTComponentType.UITableView, self.Args)
        
    def SelectIndex(self):
        '''
        select a row in a table view by [row_id, section_id]
        '''
        self.mtdriver.execute("*", "SelectIndex", MTComponentType.UITableView, self.Args)
        
    def EnterDateAndTime(self):
        '''
        pick a date and time from date picker
        '''
        self.mtdriver.execute(self.MonkeyID, "EnterDateAndTime", MTComponentType.UIDatePicker, self.Args)
        
    def Clear(self):
        '''
        simulate "close" button to clear text
        '''
        self.mtdriver.execute(self.MonkeyID, "Clear", MTComponentType.UITextField)
        
    def Open(self):
        '''
        open a link from web page
        '''
        self.mtdriver.execute(self.MonkeyID, "Open", "Link", self.Args)
        
    def Click(self):
        '''
        Only for webview, elements can be located by xpath
        '''
        self.mtdriver.execute(self.MonkeyID, "Click", "")   

    def ExtCommand(self, action, value):
        '''
        execute extended command
        '''
        self.Args = value
        self.mtdriver.execute(self.MonkeyID, action, MTComponentType.Extend, self.Args)   
