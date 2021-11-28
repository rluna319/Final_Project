# from multiprocessing import Pool

# def f(x):
#     return x*x

# if __name__ == '__main__':
#     p = Pool(5)
#     print(p.map(f, [1, 2, 3]))

########################################################################################

# from multiprocessing import Process
# import os

# def info(title):
#     print (title)
#     print ('module name:', __name__)
#     if hasattr(os, 'getppid'):  # only available on Unix
#         print ('parent process:', os.getppid())
#     print ('process id:', os.getpid())

# def f(name):
#     info('function f')
#     print ('hello', name)

# if __name__ == '__main__':
#     info('main line')
#     p = Process(target=f, args=('bob',))
#     p.start()
#     p.join()

########################################################################################

from multiprocessing import Pool, TimeoutError
import time
import os

def f(x):
    return x*x

if __name__ == '__main__':
    pool = Pool(processes=4)              # start 4 worker processes

    # print "[0, 1, 4,..., 81]"
    print (pool.map(f, range(10)))

    # print same numbers in arbitrary order
    for i in pool.imap_unordered(f, range(10)):
        print (i)

    # evaluate "f(20)" asynchronously
    res = pool.apply_async(f, (20,))      # runs in *only* one process
    print (res.get(timeout=1))              # prints "400"

    # evaluate "os.getpid()" asynchronously
    res = pool.apply_async(os.getpid, ()) # runs in *only* one process
    print (res.get(timeout=1))              # prints the PID of that process

    # launching multiple evaluations asynchronously *may* use more processes
    multiple_results = [pool.apply_async(os.getpid, ()) for i in range(4)]
    print ([res.get(timeout=1) for res in multiple_results])