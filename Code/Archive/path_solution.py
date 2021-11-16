from pathlib import Path, PureWindowsPath
import os
from PIL import Image
import glob
import numpy as np

#global path definitions
O_path = Path("Original_Images/")
E_path = Path("Encrypted_Images/")
D_path = Path("Decrypted_Images/")
path = Path("Test/")

# Wrapper for PIL images 
class Image_Data:
    def __init__(self, image):
        self.image = image
        self.f_name = image.filename
        self.b_array = np.array(image).tobytes()
        self.shape = np.array(image).shape
        self.datatype = np.array(image).dtype.name

# Generate Image_Data list
def get_images(path):
    img_dir = path
    data_path = os.path.join(img_dir,'*g') 
    files = glob.glob(data_path) 
    img_arr = []

    # loop through the images and append the newly created PIL image to the Image_Data list
    for f in files:
        img = Image.open(f)
        img_arr.append(Image_Data(img))

    return img_arr

images = get_images(path)

print("Number of images: "+str(len(images)))
print()
print("Image path: "+images[0].f_name)
print("Pure Windows Conversion: "+str(PureWindowsPath(images[0].f_name)))
print()
print("If these are the same (on Windows), then i think we have our problem solved..")