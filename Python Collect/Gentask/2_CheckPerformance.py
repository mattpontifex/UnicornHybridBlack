from Engine.checkperformance import performancereporter
from tkinter import Tk     # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename

class Engine():
    def __init__(self):
        self.finished = True
        
if __name__ == "__main__":

    task = Engine()
    root = Tk()
    root.withdraw()
    filename = askopenfilename(filetypes=[("PythonCollect", "*.psydat"),("OddballTask", "OB*.psydat"), ("FlankerTask", "FT*.psydat"), ("N2backTask", "N2B*.psydat"), ("ContN2backTask", "CN2B*.psydat"), ("All", "*")])  # show an "Open" dialog box and return the path to the selected file
    root.destroy()
    task.outputfile = filename.split('.')[0] + '.psydat'
    
    performancereporter(task)
