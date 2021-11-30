import multiprocessing as mp
import time

class Process(mp.Process):
    def __initi__(self,id):
        super(Process, self).__init__()
        self.id = id

        def run(self):
            time.sleep(1)
            print("I'm the process with id: {}".format(self.id))

# Wrapper for PIL images 
class Tile_Data:
    def __init__(self, image, num):
        self.image = image
        self.b_array = np.array(image).tobytes()
        self.shape = np.array(image).shape
        self.datatype = np.array(image).dtype.name
        self.tileNumber = num

def square(x):
    start = time.time()
    time.sleep(1)
    out = x*x
    finish = time.time()
    return [x*x, round(finish-start, 4)]

if __name__ == '__main__':
    pool = mp.Pool()
    pool = mp.Pool(processes = 4)
    inputs = [0,1,2,3,4]
    outputs_async = pool.map_async(square,inputs)
    outputs = outputs_async.get()
    pool.close()
    print ("Input: {}".format(inputs))
    print ("Output: {}".format(outputs))