from Engine.unicornhybridblackviewer import Viewer

if __name__ == "__main__":
    # Unicorn multiprocessing will not run in Spyder 
    # Run -> Configuration per file... 
    # Change the Console to Execute in an external system terminal
    # Select the checkbox for External system terminal Interact with the Python console after execution
    
    task = Viewer()

    task.unicornchannels = 'FZ, FC1, FC2, CP3, CPZ, CP4, PZ, POZ, AccelX, AccelY, AccelZ, GyroX, GyroY, GyroZ, Battery, Sample'
    with open('UnicornDeviceID.txt', 'r') as f:
        task.unicorn = f.read(); f.close()
    task.updatetime = 500 # make larger if app starts hanging
    task.run()