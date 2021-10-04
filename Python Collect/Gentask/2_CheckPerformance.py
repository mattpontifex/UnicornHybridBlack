from Engine.basicstimuluspresentationengine import Engine
from Engine.checkperformance import performancereporter
from tkinter import Tk     # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename

if __name__ == "__main__":

    task = Engine()
    task.finished = True
    Tk().withdraw() 
    filename = askopenfilename(filetypes=[("PythonCollect", "*.psydat"),("OddballTask", "OB*.psydat"), ("FlankerTask", "FT*.psydat"), ("N2backTask", "N2B*.psydat"), ("ContN2backTask", "CN2B*.psydat"), ("All", "*")])  # show an "Open" dialog box and return the path to the selected file
    task.outputfile = filename.split('.')[0] + '.psydat'
    
    performancereporter(task, show=True)
    