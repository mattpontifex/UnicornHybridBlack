import tkinter    # from tkinter import Tk for Python 3.x
import tkinter.ttk 
import numpy
from sys import platform
import os
import subprocess

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
        self._close = False
    
    def show(self):
        # creating tkinter window
        self.window = tkinter.Tk()
        self.window.lift()
        self.window.wm_attributes('-topmost',1)
        self.window.title('Unicorn Hybrid Black Task Selector')
        self.winsize = [400, 300]
        
        #self.window.attributes("-fullscreen", 1)
    
        #TK approach is to create then place
        headerpadwin = tkinter.Frame(master=self.window, width=self.winsize[0], height=numpy.multiply(self.winsize[1],0.1), bg="white")
        headerwin = tkinter.Frame(master=self.window, width=self.winsize[0], height=numpy.multiply(self.winsize[1],0.1), bg="white")
        mainwin = tkinter.Frame(master=self.window, width=self.winsize[0], height=numpy.multiply(self.winsize[1],0.1), bg="white")
        footerwin = tkinter.Frame(master=self.window, width=self.winsize[0], height=numpy.multiply(self.winsize[1],0.1), bg="white")
        footerpadwin = tkinter.Frame(master=self.window, width=self.winsize[0], height=numpy.multiply(self.winsize[1],0.1), bg="white")
        
        frame = tkinter.Frame(self.window, bg="white", borderwidth=0, highlightthickness=0)
        if platform == "linux" or platform == "linux2" or platform == "darwin":
            # OS X
            self.canvas = tkinter.Canvas(frame, bg="white", width=self.winsize[0], height=numpy.multiply(self.winsize[1],0.7),borderwidth=0, highlightthickness=0)
        elif platform == "win32":
            self.canvas = tkinter.Canvas(frame, bg="white", width=self.winsize[0]*1.1, height=numpy.multiply(self.winsize[1],0.7),borderwidth=0, highlightthickness=0)
        
        headerpadwintext = tkinter.Label(master=headerwin, text='', fg='gray', font=(None, 5), bg="white",
                                 justify='center', anchor='center', 
                                 width=int(numpy.multiply(self.winsize[0],0.9)))
        
        headerwinbutton = tkinter.Button(master=headerwin, text='Check Signal from Unicorn Hybrid Black', font=(None, 25), 
                                 justify='center', anchor='center', bd = 0,
                                 fg='#FFFFFF', bg="#3D5E73",
                                 activeforeground='#FFFFFF', activebackground='#004F39',
                                 width=int(numpy.multiply(self.winsize[0],0.05)),
                                 relief='flat', underline=-1, 
                                 command=self.headerwinbuttonhit)
        
        
        footerwinbutton = tkinter.Button(master=footerwin, text='Recheck Task Performance', font=(None, 15), 
                                 justify='center', anchor='center', bd = 0,
                                 fg='#FFFFFF', bg="#3D5E73",
                                 activeforeground='#FFFFFF', activebackground='#004F39',
                                 width=int(numpy.multiply(self.winsize[0],0.05)),
                                 relief='flat', underline=-1, 
                                 command=self.footerwinbuttonhit)
        
        # place
        placen = 0
        headerpadwintext.grid(row=placen, column=0, sticky="nsew")
        headerpadwin.grid(row=placen, column=0, sticky="nsew"); placen = placen + 1
        self.window.rowconfigure(0, weight=0, minsize=numpy.multiply(self.winsize[1],0.05))
        
        headerwinbutton.grid(row=placen, column=0, sticky="nsew")
        headerwin.grid(row=placen, column=0, sticky="nsew"); placen = placen + 1
        self.window.rowconfigure(0, weight=0, minsize=numpy.multiply(self.winsize[1],0.15))
        
        mainwin.grid(row=placen, column=0, sticky="nsew"); placen = placen + 1
        self.window.rowconfigure(0, weight=0, minsize=numpy.multiply(self.winsize[1],0.6))
        
        footerwinbutton.grid(row=placen, column=0, sticky="nsew")
        footerwin.grid(row=placen, column=0, sticky="nsew"); placen = placen + 1
        self.window.rowconfigure(0, weight=0, minsize=numpy.multiply(self.winsize[1],0.15))
        
        footerpadwin.grid(row=placen, column=0, sticky="nsew"); placen = placen + 1
        self.window.rowconfigure(0, weight=0, minsize=numpy.multiply(self.winsize[1],0.05))
        
        [x, y] = centerprompt(self.window)
        self.window.geometry("+%d+%d" % (x, y))
        
        self.window.mainloop()
        
    def headerwinbuttonhit(self): 
        self.close()
        try:
            output = subprocess.call(['python', '1_CheckSignal.py'])
        except:
            os.chdir(os.path.dirname(os.getcwd()))
            output = subprocess.call(['python', '1_CheckSignal.py'])
    

    def footerwinbuttonhit(self): 
        self.close()
        try:
            output = subprocess.call(['python', '2_CheckPerformance.py'])
        except:
            os.chdir(os.path.dirname(os.getcwd()))
            output = subprocess.call(['python', '2_CheckPerformance.py'])
            
    def close(self):
        self._close = True
        self.window.destroy()
        
if __name__ == "__main__":

    task = selectscreen()
    task.show()