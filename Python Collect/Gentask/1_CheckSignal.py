from Engine.checksignal import checksignal

if __name__ == "__main__":
    task = checksignal()
    task.channellabels = ['FCZ', 'C3', 'CZ', 'C4', 'PZ', 'O1', 'OZ', 'O2']
    task.unicorn = 'UN-2019.05.51' 
    task.controlband = [20, 40] # hz
    task.noiseband = [58, 62] # hz
    
    task.start()