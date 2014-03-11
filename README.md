#mtdriver

A python binding for monkeytalk protocol

##Usage
```
from MTDriver.MTDriver import MTDriver
from MTDriver import MTException, MTElement, MTComponentType, MTProperty
mt = MTDriver("localhost:16863")
btnConfirm = MTElement(self, MTComponentType.UIButton,"Confirm")
btnConfirm.Tap()
```
