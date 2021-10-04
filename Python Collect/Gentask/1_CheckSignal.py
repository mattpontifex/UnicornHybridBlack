from Engine.unicornhybridblackviewer import Viewer

if __name__ == "__main__":
    # Unicorn multiprocessing will not run in Spyder 
    # Run -> Configuration per file... 
    # Change the Console to Execute in an external system terminal
    # Select the checkbox for External system terminal Interact with the Python console after execution
    
    task = Viewer()

    task.unicornchannels = 'FZ, FC1, FC2, C3, CZ, C4, CPZ, PZ, AccelX, AccelY, AccelZ, GyroX, GyroY, GyroZ, Battery, Sample'
    task.unicorn = 'UN-2019.05.51' 
    task.updatetime = 220 # make larger if app starts hanging
    task.run()