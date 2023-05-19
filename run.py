import subprocess

#script used to run 3 files at the same time

TIME_OF_MEASUREMENT = 3600 #in seconds, for all files the same one,

proces1 = subprocess.Popen(['python', "read_filtered1.py",str(TIME_OF_MEASUREMENT)]) #runs following scripts at the same time
proces2 = subprocess.Popen(['python', "read_filtered2.py",str(TIME_OF_MEASUREMENT)])
proces3 = subprocess.Popen(['python', "read_filtered3.py",str(TIME_OF_MEASUREMENT)])

proces1.wait()
proces2.wait()
proces3.wait()
