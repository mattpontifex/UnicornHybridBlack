from Engine.unicornhybriddeviceselection import choosedevicescreen
from tkinter import Tk     # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename

        
if __name__ == "__main__":

    task = choosedevicescreen()
    task.show()
    
    with open('UnicornDeviceID.txt', 'r') as f:
        contents = f.read(); f.close()
