from PIL import Image, ImageDraw, ImageFont
import os 
import glob 
import numpy as np
import progressbar
import time

class Image_Data:
    def __init__(self, image):
        self.image = image
        self.f_name = image.filename
        self.b_array = np.array(image).tobytes()
        self.shape = np.array(image).shape
        self.datatype = np.array(image).dtype.name

img_dir = "./SmallSet_Images"
data_path = os.path.join(img_dir,'*g') 
files = glob.glob(data_path) 
data = []

widgets = ['Loading Images: ', progressbar.Bar('█'),' (', progressbar.ETA(), ') ',]
bar = progressbar.ProgressBar(28, widgets = widgets).start()
i = 0
for f in files: 
    i += 1
    img = Image.open(f)
    data.append(Image_Data(img))
    bar.update(i)

print()
print()
print("Size of data[]: "+str(len(data))+"\n")
print("Name of data[0]: "+str(data[0].f_name)+"\n")