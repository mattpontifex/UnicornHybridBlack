# -*- coding: utf-8 -*-
        
import tkinter    # from tkinter import Tk for Python 3.x
import tkinter.ttk 
from PIL import ImageTk 
import numpy
import os
import subprocess
try:
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
except:
    pass

if __name__ == "__main__":
    try:
        import UnicornPy as UnicornPy
    except:
        try:
            import Engine.UnicornPy as UnicornPy
        except:
            pass
else:
    try:
        import Engine.UnicornPy as UnicornPy
    except:
        try:
            import UnicornPy as UnicornPy
        except:
            pass

def centerprompt(toplevel):
    toplevel.update_idletasks()

    # Tkinter way to find the screen resolution
    screen_width = toplevel.winfo_screenwidth()
    screen_height = toplevel.winfo_screenheight()

    size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
    x = screen_width/2 - size[0]/2
    y = screen_height/2 - size[1]/2
    
    toplevel.geometry("+%d+%d" % (x, y))
    
    return [x, y]   
        
def writeUnicornDevice(deviceid, outputfile = []):
    f = open(outputfile, 'w')
    f.write(str(deviceid))
    f.close() # Close file

def connecttoUnicornDevice(deviceID):
    deviceconnected = 0
    try:
        device = UnicornPy.Unicorn(deviceID)
        deviceconnected = 1
        del device
    except:
        pass 
    return deviceconnected

def obtainlistofUnicornDevice():
    # Get available device serials.
    deviceList = UnicornPy.GetAvailableDevices(True)
    return deviceList


class connectdevicescreen():

    def __init__(self):
        self.deviceID = []
        self.skin = 'style1'
        self._close = False
    
    def close(self):
        self._close = True
        self.window.destroy()

    def show(self):

        deviceconnected = connecttoUnicornDevice(self.deviceID)
        
        if self.skin == 'style1':
            leftbuttoncolors = ['#4A4A4A', '#D4D4D4', '#FFFFFF', '#3D5E73']
            leftpanelcolor = ['#FFFFFF']
            rightbuttoncolors = ['#FFFFFF', '#3D5E73', '#FFFFFF', '#EF9A35']
            rightpanelcolor = ['#E0E0E0', '#4A4A4A']
            buttonstyle = ['raised', 1]
        else:
            leftbuttoncolors = ['#4A4A4A', '#D4D4D4', '#FFFFFF', '#3D5E73']
            leftpanelcolor = ['#FFFFFF']
            rightbuttoncolors = ['#4A4A4A', '#D4D4D4', '#FFFFFF', '#3D5E73']
            rightpanelcolor = ['#FFFFFF', '#4A4A4A']
            buttonstyle = ['raised', 1]
                          
        #colorsegs = ['#004F39', '#3D5E73', '#999999', '#EF9A35', '#EF6F63', '#4A4A4A', '#D4D4D4'] 
                
        # creating tkinter window
        self.window = tkinter.Tk()
        self.window.lift()
        self.window.wm_attributes('-topmost',1)
        self.window.title('Unicorn Hybrid Black Device Connection')
        self.winsize = [200, 200]
        self.window.geometry("%dx%d+0+0" % (self.winsize[0], self.winsize[1]))
        self.window.resizable(width=False,height=False)
        
        self.wsX = self.winsize[0]
        self.wsY = self.winsize[1]
        self.wsPad = [3, 3]
        self.fontsize = 15

        rightframe = tkinter.Frame(master = self.window, height=self.wsY, width=self.wsX, bg=rightpanelcolor[0])
        rightframe.pack(side='left', fill = 'both')
        rightframe.pack_propagate(0)
        

        rightframesub = []
        for cR in range(1):
            temp = tkinter.Frame(master = rightframe, height=self.wsY, bg=rightpanelcolor[0])
            temp.pack(side='top', fill = 'x', padx=self.wsPad[0], pady=self.wsPad[1])
            temp.pack_propagate(0)
            rightframesub.append(temp)
                 
        if deviceconnected == 0:
            
            rightframewintext = tkinter.Label(master=rightframesub[0], text='Unable to connect to Unicorn devices.', font=(None, self.fontsize), justify='left', anchor='sw', 
                                                      fg=rightpanelcolor[1], bg=rightpanelcolor[0])
            rightframewintext.pack(side='top', fill = 'x', padx=numpy.multiply(self.wsPad[0],5), pady=self.wsPad[1])
                        
            [x, y] = centerprompt(self.window)
            self.window.geometry("+%d+%d" % (x, y))
            self.window.mainloop()
            
        else:
            self.close()
                
        

class choosedevicescreen():
    
    def __init__(self):
        self.tasks = []
        self.taskaltlabels = []
        self.outputfile = 'UnicornDeviceID.txt'
        self.skin = 'style1'
        self._close = False
        try:
            self.tasks = obtainlistofUnicornDevice()
        except:
            self.tasks = []
        
    def close(self):
        self._close = True
        self.window.destroy()
    
    def buttonhit(self, buttoncall): 
        #print(buttoncall)
        self.close()
        if not buttoncall == '':
            writeUnicornDevice(buttoncall, outputfile = self.outputfile)
            connectdevicecheck = connectdevicescreen()
            connectdevicecheck.deviceID = buttoncall
            connectdevicecheck.show()
                    
    def show(self):
        
        if self.skin == 'style1':
            leftbuttoncolors = ['#4A4A4A', '#D4D4D4', '#FFFFFF', '#3D5E73']
            leftpanelcolor = ['#FFFFFF']
            rightbuttoncolors = ['#FFFFFF', '#3D5E73', '#FFFFFF', '#EF9A35']
            rightpanelcolor = ['#E0E0E0', '#4A4A4A']
            buttonstyle = ['raised', 1]
        else:
            leftbuttoncolors = ['#4A4A4A', '#D4D4D4', '#FFFFFF', '#3D5E73']
            leftpanelcolor = ['#FFFFFF']
            rightbuttoncolors = ['#4A4A4A', '#D4D4D4', '#FFFFFF', '#3D5E73']
            rightpanelcolor = ['#FFFFFF', '#4A4A4A']
            buttonstyle = ['raised', 1]
                          
        #colorsegs = ['#004F39', '#3D5E73', '#999999', '#EF9A35', '#EF6F63', '#4A4A4A', '#D4D4D4'] 
                
        # creating tkinter window
        self.window = tkinter.Tk()
        self.window.lift()
        self.window.wm_attributes('-topmost',1)
        self.window.title('Unicorn Hybrid Black Device Selector')
        self.winsize = [500, 550]
        self.window.geometry("%dx%d+0+0" % (self.winsize[0], self.winsize[1]))
        self.window.resizable(width=False,height=False)
        
        self.wsX = self.winsize[0]
        self.wsY = self.winsize[1]
        self.wsPad = [3, 3]
        self.fontsize = 15
        
        # note design
        # two column (40 60 split)
        # Column 0: 3 rows
        # Column 1: X rows
        
        
        rightframe = tkinter.Frame(master = self.window, height=self.wsY, width=self.wsX, bg=rightpanelcolor[0])
        rightframe.pack(side='left', fill = 'both')
        rightframe.pack_propagate(0)
        
        self.wsPad = [6, 6]
        if len(self.tasks) > 0:
            
            if len(self.taskaltlabels) == 0:
                for cR in range(len(self.tasks)):
                    self.taskaltlabels.append(self.tasks[cR])
        
        wsYsub = [numpy.divide(self.wsY, (len(self.tasks)+1))] * (len(self.tasks)+1)
        wsYsub[0] = numpy.multiply(self.wsY,0.1)
        rightframesub = []
        for cR in range(len(self.tasks)+1):
            temp = tkinter.Frame(master = rightframe, height=wsYsub[cR], bg=rightpanelcolor[0])
            temp.pack(side='top', fill = 'x', padx=self.wsPad[0], pady=self.wsPad[1])
            temp.pack_propagate(0)
            rightframesub.append(temp)
        
        if len(self.tasks) > 0:
            rightframewintext = tkinter.Label(master=rightframesub[0], text='Available Devices:', font=(None, self.fontsize), justify='left', anchor='sw', 
                                              fg=rightpanelcolor[1], bg=rightpanelcolor[0])
            rightframewintext.pack(side='top', fill = 'x', padx=numpy.multiply(self.wsPad[0],5), pady=self.wsPad[1])
        
            rightbuttons = []
            for cR in range(1, len(self.tasks)+1):
                temp = tkinter.Button(master=rightframesub[cR], text=self.taskaltlabels[cR-1], font=(None, self.fontsize), 
                             justify='center', anchor='center', bd = buttonstyle[1],
                             fg=rightbuttoncolors[0], bg=rightbuttoncolors[1],
                             activeforeground=rightbuttoncolors[2], activebackground=rightbuttoncolors[3],
                             relief=buttonstyle[0], underline=-1, 
                             command=lambda port = self.tasks[cR-1]: self.buttonhit(port))
                temp.pack(side='top', fill = 'x', padx=numpy.multiply(self.wsPad[0],10.0), pady=self.wsPad[1], ipady=numpy.multiply(self.fontsize, 0.7))
                temp.pack_propagate(0)
                rightbuttons.append(temp)
                
        else:
            rightframewintext = tkinter.Label(master=rightframesub[0], text='No Unicorn Devices Found', font=(None, self.fontsize), justify='left', anchor='sw', 
                                              fg=rightpanelcolor[1], bg=rightpanelcolor[0])
            rightframewintext.pack(side='top', fill = 'x', padx=numpy.multiply(self.wsPad[0],5), pady=self.wsPad[1])
            
        [x, y] = centerprompt(self.window)
        self.window.geometry("+%d+%d" % (x, y))
        self.window.mainloop()
        
if __name__ == "__main__":

    task = choosedevicescreen()
    task.show()
