from Engine.checkperformance import performancereporter
from tkinter import Tk     # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename

class Engine():
    def __init__(self):
        self.finished = True
        
if __name__ == "__main__":

    task = Engine()
    root = Tk()
    root.lift()
    root.wm_attributes('-topmost',1)
    root.withdraw()
    filename = askopenfilename(filetypes=[("PythonCollect", "*.psydat"),("EyesClosedTask", "EC*.psydat"),("OddballTask", "OB*.psydat"), ("FlankerTask", "FT*.psydat"), ("NogoTask", "GNG*.psydat"), ("N2backTask", "N2B*.psydat"), ("ContN2backTask", "CN2B*.psydat"), ("All", "*")])  # show an "Open" dialog box and return the path to the selected file
    root.destroy()
    if len(filename) > 0:
        task.outputfile = filename.split('.')[0] + '.psydat'
        performancereporter(task)
