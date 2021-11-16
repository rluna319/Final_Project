import numpy as np

array = [['a', 2], ['b', 4], ['c', 8]]

results = list(zip(*array))

result = sum(results[1])
print("Result: {}".format(result))