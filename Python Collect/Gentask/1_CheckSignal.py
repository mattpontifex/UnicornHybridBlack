from Engine.unicornhybridblackviewer import Viewer

if __name__ == "__main__":
    # Unicorn multiprocessing will not run in Spyder 
    # Run -> Configuration per file... 
    # Change the Console to Execute in an external system terminal
    # Select the checkbox for External system terminal Interact with the Python console after execution
    
    task = Viewer()
    #task.channellabels = ['FCZ', 'CP1', 'CPZ', 'CP2', 'P1', 'PZ', 'P2', 'OZ']
    #task.channellabels = ['FZ', 'FCZ', 'C3', 'CZ', 'C4', 'CPZ', 'PZ', 'POZ']
    task.channellabels = ['FZ', 'FC1', 'FC2', 'C3', 'CZ', 'C4', 'CPZ', 'PZ']
    task.unicorn = 'UN-2019.05.51' 
    task.updatetime = 220 # make larger if app starts hanging
    task.run()