import tkinter    # from tkinter import Tk for Python 3.x
import tkinter.ttk 
from PIL import ImageTk 
import numpy
from sys import platform
import os
import subprocess
try:
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
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

        
class selectscreen():
    
    def __init__(self):
        self.controls = []
        self.tasks = []
        self.taskaltlabels = []
        self._close = False
        
    def close(self):
        self._close = True
        self.window.destroy()
    
    def buttonhit(self, buttoncall): 
        self.close()
        try:
            output = subprocess.call(['python', buttoncall])
        except:
            os.chdir(os.path.dirname(os.getcwd()))
            output = subprocess.call(['python', buttoncall])
            
    def show(self):
        
        # creating tkinter window
        self.window = tkinter.Tk()
        self.window.lift()
        self.window.wm_attributes('-topmost',1)
        self.window.title('Unicorn Hybrid Black Task Selector')
        self.winsize = [900, 550]
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
        
        leftframe = tkinter.Frame(master = self.window, height=self.wsY, width=numpy.multiply(self.wsX,0.35), bg="white")
        leftframe.pack(side='left', fill = 'both')
        leftframe.pack_propagate(0)
        
        self.wsPad = [3, 3]
        wsYsub = [0,0,0]
        wsYsub[0] = numpy.multiply(self.wsY,0.2)
        wsYsub[1] = numpy.multiply(self.wsY,0.4)
        wsYsub[2] = numpy.multiply(self.wsY,0.4)
        wsYpack = ['bottom'] * 3
        wsYpack[1] = 'top'
        leftframesub = []
        for cR in range(3):
            temp = tkinter.Frame(master = leftframe, height=wsYsub[cR], bg="white")
            temp.pack(side=wsYpack[cR], fill = 'x', padx=self.wsPad[0], pady=self.wsPad[1])
            temp.pack_propagate(0)
            leftframesub.append(temp)
        
        
        
        canvas = tkinter.Canvas(leftframesub[1], bg="white", borderwidth=0, highlightthickness=0)
        canvas.pack(side='bottom', fill = 'x')
        canvas.pack_propagate(0)
        photoimage = []
        try:
            photoimage = ImageTk.PhotoImage(file="eggheadframe1.png")
        except:
            try:
                photoimage = ImageTk.PhotoImage(file="Engine" + os.path.sep + "eggheadframe1.png")
            except:
                photoimage = ImageTk.PhotoImage(file="Gentask" + os.path.sep + "Engine" + os.path.sep + "eggheadframe1.png")
        
        canvas.create_image(150, 50, image=photoimage, anchor="n")
        
        
        leftbuttons = []
        temp = tkinter.Button(master=leftframesub[2], text='Check EEG Signal', font=(None, self.fontsize), 
                             justify='center', anchor='center', bd = 0,
                             fg='#4A4A4A', bg="#D4D4D4",
                             activeforeground='#FFFFFF', activebackground='#3D5E73',
                             relief='flat', underline=-1, 
                             command=lambda: self.buttonhit(self.controls[0]))
        temp.pack(side='top', fill = 'x', padx=self.wsPad[0], pady=self.wsPad[1], ipady=numpy.multiply(self.fontsize, 0.7))
        temp.pack_propagate(0)
        leftbuttons.append(temp)
        
        
        temp = tkinter.Button(master=leftframesub[0], text='Recheck Task Performance', font=(None, int(numpy.multiply(self.fontsize,0.8))), 
                             justify='center', anchor='center', bd = 0,
                             fg='#4A4A4A', bg="#D4D4D4",
                             activeforeground='#FFFFFF', activebackground='#3D5E73',
                             relief='flat', underline=-1,
                             command=lambda: self.buttonhit(self.controls[1]))
        temp.pack(side='bottom', fill = 'x', padx=self.wsPad[0], pady=self.wsPad[1], ipady=numpy.multiply(self.fontsize, 0.7))
        temp.pack_propagate(0)
        leftbuttons.append(temp)
        
        
        
        
        rightframe = tkinter.Frame(master = self.window, height=self.wsY, width=numpy.multiply(self.wsX,0.65), bg="white")
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
                temp = tkinter.Frame(master = rightframe, height=wsYsub[cR], bg="white")
                temp.pack(side='top', fill = 'x', padx=self.wsPad[0], pady=self.wsPad[1])
                temp.pack_propagate(0)
                rightframesub.append(temp)
            
            rightframewintext = tkinter.Label(master=rightframesub[0], text='Available Tasks:', font=(None, self.fontsize), justify='left', anchor='w', 
                                              fg='#000000', bg="white")
            rightframewintext.pack(side='top', fill = 'x', padx=numpy.multiply(self.wsPad[0],5), pady=self.wsPad[1])
        
            rightbuttons = []
            for cR in range(1, len(self.tasks)+1):
                temp = tkinter.Button(master=rightframesub[cR], text=self.taskaltlabels[cR-1], font=(None, self.fontsize), 
                             justify='center', anchor='center', bd = 0,
                             fg='#4A4A4A', bg="#D4D4D4",
                             activeforeground='#FFFFFF', activebackground='#3D5E73',
                             relief='flat', underline=-1, 
                             command=lambda: self.buttonhit(self.tasks[cR-1]))
                temp.pack(side='top', fill = 'x', padx=numpy.multiply(self.wsPad[0],10.0), pady=self.wsPad[1], ipady=numpy.multiply(self.fontsize, 0.7))
                temp.pack_propagate(0)
                rightbuttons.append(temp)
        
        [x, y] = centerprompt(self.window)
        self.window.geometry("+%d+%d" % (x, y))
        self.window.mainloop()
        
if __name__ == "__main__":

    task = selectscreen()
    task.controls = ['1_CheckSignal.py', '2_CheckPerformance.py']
    task.tasks = ['FlankerTask.py', 'OddballTask.py', 'NbackTask_2back.py', 'ContinuousNbackTask_2back.py']
    task.taskaltlabels = ['Flanker Arrow Task', 'Oddball Detection Task', '2 Back Task', 'Continuous 2 Back Task']
    task.show()