import Engine.taskselectionwindow as taskselectionwindow
        
if __name__ == "__main__":

    task = taskselectionwindow.selectscreen()
    task.controls = ['1_CheckSignal.py', '3_ChangeDevice.py', '2_CheckPerformance.py']
    task.tasks = ['EyesClosed.py', 'OddballTask.py', 'FlankerPractice.py', 'FlankerTask.py', 'NogoPractice.py', 'NogoTask.py']
    task.taskaltlabels = ['Eyes Closed', 'Oddball Task', 'Flanker Arrow Practice', 'Flanker Arrow Task', 'Nogo Practice', 'Nogo Task']
    task.show()
