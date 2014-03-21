'''
Created on Mar 6, 2013

@author: mxu
'''
class MTException:
    class NoComponentTypeError(Exception):
        def __init__(self, message):
            self.message = message
        def __str__(self):
            return repr('Error: ' + self.message)
            
    class NoMonkeyIDError(Exception):
        def __init__(self, message):
            self.message = message
        def __str__(self):
            return repr('Error: ' + self.message)    
            
    class NoMTDriverInstanceError(Exception):
        def __init__(self, message):
            self.message = message
        def __str__(self):
            return repr('Error: ' + self.message) 
            
    class TimeoutError(Exception):
        def __init__(self, message):
            self.message = message
        def __str__(self):
            return repr(self.message)
            
    class CrashError(Exception):
        def __init__(self, message):
            self.message = message
        def __str__(self):
            return repr(self.message)     
    class TooManyFailedActionsError(Exception):
        def __init__(self, message):
            self.message = message
        def __str__(self):
            return repr(self.message)   