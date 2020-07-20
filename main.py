'''
Diego CB - 2020-06-21
Windows only
'''
import os
import math
import glob
from datetime import datetime
import wx
from io import BytesIO
import win32clipboard
import win32gui
import win32con
import win32api
from PIL import Image
import pyautogui
import mouse
import warnings
warnings.filterwarnings("ignore")

class frameScreenshot(wx.Frame):

    def __init__(self, parent, id):        
        self.hsave = 0
        self.x1 = 0
        self.x2 = 0
        self.y1 = 0
        self.y2 = 0

        cwd = os.getcwd()
        screen_nome = datetime.timestamp(datetime.now())
        self.filepath = cwd+'\\'+str(screen_nome)+'.png'
        wx.Frame.__init__(self, parent, id, 'Zurata Print', size=(280,230), style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        items = ['P&B','RGB']
        self.comboColor = wx.ComboBox(panel, -1, size=(230, 40), style = wx.CB_READONLY)
        for s in items: 
            self.comboColor.Append(s)
        self.comboColor.SetSelection(0)
        vbox.Add(self.comboColor, 0,  wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 20)
        
        items = ['100%','75%','50%','25%']
        self.comboQuality = wx.ComboBox(panel, -1, size=(230, 40), style = wx.CB_READONLY)
        for s in items:
            self.comboQuality.Append(s)
        self.comboQuality.SetSelection(0)
        vbox.Add(self.comboQuality, 0,  wx.ALIGN_CENTER_HORIZONTAL, 20)
        
        self.btn = wx.Button(panel, label = 'Capture screen', pos = (15,70), size=(230, 40))
        self.btn.Bind(wx.EVT_BUTTON, self.onBtnClick)
        vbox.Add(self.btn,0,  wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 20)
        
        panel.SetSizer(vbox)

    def drawCross(self, x, y):
        dc = win32gui.GetDC(0)
        red = win32api.RGB(255, 0, 0)
        cont  = x - 5
        while cont < x + 5:
            win32gui.SetPixel(dc, cont, y, red)
            cont  = cont + 1
        cont2 = y - 5
        while cont2 < y + 5:
            win32gui.SetPixel(dc, x, cont2, red)
            cont2 = cont2 + 1
 
    def genImage(self):
        x1 = str(self.x1).rjust(4)        
        y1 = str(self.y1).rjust(4)        
        x2 = str(self.x2).rjust(4)        
        y2 = str(self.y2).rjust(4)

        screen = wx.ScreenDC()
        size = screen.GetSize()
        bmp = wx.EmptyBitmap(size[0], size[1])
        mem = wx.MemoryDC(bmp)
        mem.Blit(0, 0, size[0], size[1], screen, 0, 0)
        del mem
        bmp.SaveFile(self.filepath, wx.BITMAP_TYPE_PNG)

        if(self.comboColor.GetValue()=='RGB'):
            foo = Image.open(self.filepath)
        else:
            foo = Image.open(self.filepath).convert('LA')

        x, y = foo.size

        if(self.comboQuality.GetValue()=='100%'):
            x_percent = 0
            y_percent = 0
        elif(self.comboQuality.GetValue()=='75%'):
            x_percent = x * 0.25
            y_percent = y * 0.25
        elif(self.comboQuality.GetValue()=='50%'):
            x_percent = x * 0.50
            y_percent = y * 0.50
        elif(self.comboQuality.GetValue()=='25%'):
            x_percent = x * 0.75
            y_percent = y * 0.75

        x3, y3 = math.floor(x - x_percent), math.floor(y - y_percent)
        foo = foo.resize((x3,y3),Image.NEAREST)
            
        img_quality = 0

        left = int(x1)
        top = int(y1)
        right = int(x3)
        bottom = int(y3)

        if left > right:
            aux = left
            left = right
            right = aux
    
        if top > bottom:
            aux = top
            top = bottom
            bottom = aux
    
        foo = foo.crop((left, top, right, bottom))        
        output = BytesIO()
        foo.save(self.filepath, optimize=True, quality=img_quality)
        foo.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]
        output.close()
        
        self.copyToClipboard(data)
        
        '''os._exit(0)
        self.cropImage(x1, y1, x2, y2, img_quality)'''
        


    def copyToClipboard(self, data):
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()
        self.btn.SetLabel("Captured!")
        os._exit(0)

    def onMouseClick(self):
        if self.cont_mouse == 0:
            self.x1, self.y1 = pyautogui.position()
            x = self.x1
            y = self.y1
            self.drawCross(x, y)            
            self.btn.SetLabel("Click B")
        elif self.cont_mouse == 1:
            self.x2, self.y2 = pyautogui.position()
            x = self.x2
            y = self.y2
            self.drawCross(x, y)
            self.genImage()            
        self.cont_mouse = self.cont_mouse + 1
            
    def onBtnClick(self, e):
        self.btn.SetLabel("Click A")
        mouse.on_click(lambda: self.onMouseClick())
        self.cont_mouse = 0

if __name__ =='__main__':
        files = glob.glob(os.getcwd()+'//*.png')
        for f in files:
            try:
                os.remove(f)
            except OSError as e:
                print("Error: %s : %s" % (f, e.strerror))
        app = wx.PySimpleApp()
        frame = frameScreenshot(parent=None, id=-1)
        frame.Show()
        app.MainLoop()    

