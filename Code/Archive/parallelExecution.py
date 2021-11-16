# importing os module 
import os
import threading
import time
import random
import image_slicer

# Get the number of CPUs
# in the system using
# os.cpu_count() method
cpuCount = os.cpu_count()

exitFlag = 0

class encryptionThread (threading.Thread):
   def __init__(self, threadID, chunk):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.chunk = chunk
   def run(self):
      print ("Starting encryption on chunk " + str(self.threadID) + "\n")
      encrypt_chunk()
      print ("Finished encrypting chunk " + str(self.threadID) + "\n")

def encrypt_chunk():
   #print("Encrypting")
   time.sleep(random.randint(1, 5))

  
# Print the number of
# CPUs in the system
print("Number of CPUs in the system:", cpuCount)

threads = []
for thread in range(cpuCount):
    newThread = encryptionThread(thread, "010010101")
    newThread.start()
    threads.append(newThread)