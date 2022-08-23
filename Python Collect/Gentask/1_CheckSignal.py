from Engine.unicornhybridblackviewer import Viewer

if __name__ == "__main__":
    # Unicorn multiprocessing will not run in Spyder 
    # Run -> Configuration per file... 
    # Change the Console to Execute in an external system terminal
    # Select the checkbox for External system terminal Interact with the Python console after execution
    
    task = Viewer()

    task.unicornchannels = 'FP1, FFC1, FFC2, FCZ, CPZ, CPP1, CPP2, PZ, AccelX, AccelY, AccelZ, GyroX, GyroY, GyroZ, Battery, Sample'
    with open('UnicornDeviceID.txt', 'r') as f:
        task.unicorn = f.read(); f.close()
    with open('UnicornDeviceChannels.txt', 'r') as f:
        task.unicornchannels  = f.read(); f.close()
    #task.unicorn = 'UN-2021.05.40' 
    task.updatetime = 500 # make larger if app starts hanging
    task.run()
