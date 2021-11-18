#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cryptography.fernet import Fernet
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import io
import os
import glob
import math
import time
import progressbar
from pathlib import Path
import shutil

#global path definitions
O_path = Path("Original_Images")
E_path = Path("Encrypted_Images")
D_path = Path("Decrypted_Images")
# img_dir = Path("Test")
img_dir = Path("SmallSet_Images")
# img_dir = Path("Sample_Images")

# Font for ImageDraw
myFont = Path("Fonts") / "Teletactile.ttf"

# Wrapper for PIL images 
class Image_Data:
    def __init__(self, image, filename):
        self.image = image
        self.f_name = filename
        self.b_array = np.array(image).tobytes()
        self.shape = np.array(image).shape
        self.datatype = np.array(image).dtype.name

# Generate Image_Data list
def get_images(path):
    files = path.glob('*g')
    img_arr = []

    # initialize a progress bar for loading images
    widgets = ['Loading Images... ', progressbar.AnimatedMarker()]
    bar = progressbar.ProgressBar(widgets = widgets).start()
    i = 0

    # loop through the images and append the newly created PIL image to the Image_Data list
    for f in files:
        i += 1 
        img = Image.open(f)
        img_arr.append(Image_Data(img, f.name))
        bar.update(i)
    print("\n\n")

    return img_arr

# Fernent setup
def get_key():
    key = Fernet.generate_key()
    with open('secret.key', 'wb') as new_key_file:
        new_key_file.write(key)

    print("Key: " + str(key) + "\n")

    return Fernet(key)

# Create/Empty directories for the (marked) original images, encrypted images, and decrypted images
# Note that the images have the same original filenames to keep track
def setup_directories():
    if O_path.is_dir():
        try:
            shutil.rmtree(O_path)
            os.mkdir(O_path)
        except OSError as e:
            print("Error: %s : %s" % (O_path.name, e.strerror))
    else:
        try:
            os.mkdir(O_path)
        except OSError as e:
            print("Error: %s : %s" % (O_path.name, e.strerror))

    if E_path.is_dir():
        try:
            shutil.rmtree(E_path)
            os.mkdir(E_path)
        except OSError as e:
            print("Error: %s : %s" % (E_path.name, e.strerror))
    else:
        try:
            os.mkdir(E_path)
        except OSError as e:
            print("Error: %s : %s" % (E_path.name, e.strerror))

    if D_path.is_dir():
        try:
            shutil.rmtree(D_path)
            os.mkdir(D_path)
        except OSError as e:
            print("Error: %s : %s" % (D_path.name, e.strerror))
    else:
        try:
            os.mkdir(D_path)
        except OSError as e:
            print("Error: %s : %s" % (D_path.name, e.strerror))

# Helper function for build_and_save()
# Write text on the images and save them to their respective directories
def label_and_save(image, label, filename, save_dir):
    d = ImageDraw.Draw(image)
    d.text((28,36), label, font=ImageFont.truetype(font=str(myFont), size = 80), fill=(255,0,0))
    image.save(str(save_dir / filename))

# Create the images from the bytearray and save them to their respective directories for logging
def build_and_save(i_data, b_text, mode):
    if mode == 0: # encrypted image
        c_size = len(b_text)
        c_pixels = int((c_size+2)/3)
        W = H = int(math.ceil(c_pixels ** 0.5))

        data = b_text + b'\0' * (W*H*3 - len(b_text))
        cypherpic = Image.frombytes('RGB', (W, H), data)
        label_and_save(cypherpic, "Encrypted Image", i_data.f_name, E_path)
    elif mode == 1: #decrypted image
        output = Image.fromarray(np.frombuffer(b_text, dtype=i_data.datatype).reshape(i_data.shape))
        label_and_save(output, "Decrypted Image", i_data.f_name, D_path)

# Encrypt plaintext and get execution time
def encrypt(message, F):
    timer1 = time.time()
    c_text = F.encrypt(message)
    extime = round(time.time() - timer1, 4)

    return c_text, extime

# Decrypt cyphertext and get execution time
def decrypt(cypher, F):
    timer2 = time.time()
    p_text = F.decrypt(cypher)
    extime = round(time.time() - timer2, 4)

    return p_text, extime

# print out the number of images used, and the average encryption and decryption times with a decimal precision of 4
def print_results(num_images, e_times, d_times):
    print("Number of images: "+str(num_images)+"\n")
    print("Average Encryption Time: "+str(round(np.mean(e_times), 4))+" seconds\n")
    print("Average Decryption Time: "+str(round(np.mean(d_times), 4))+" seconds\n")

# main driver code
def main():

    # create images list
    images = get_images(img_dir)

    # if directories already exist, empty them, else create them
    setup_directories()

    # get the key
    k = get_key()

    # initialize lists to hold execution times of encryption and decryption
    enc_times = []
    dec_times = []

    # initialize a progress bar for loading images
    widgets = ['Batch Encryption/Decryption... ', progressbar.AnimatedMarker()]
    bar = progressbar.ProgressBar(widgets = widgets).start()
    t = 0

    # loop through loaded images and run encryption and decryption
    # timing information is gathered in the encrypt() and decrypt() functions
    for i in images:

        t += 1

        # mark and save the input image to the respective directory
        label_and_save(i.image, "Orignial Image", i.f_name, O_path)

        # initialize message variable for input to encryption function
        msg = i.b_array

        # get the cyphertext and the execution time from the encryption function
        cyphertext, encryption_time = encrypt(msg, k)
        # append the execution time to the respective list
        enc_times.append(encryption_time)
        # create an image from the cyphertext and save it to its respective directory
        build_and_save(i, cyphertext, 0)

        # get the cleartext (decrypted bytearray/text) and the execution time from the decryption function
        cleartext, decryption_time = decrypt(cyphertext, k)
        # append the execution time to the respective list
        dec_times.append(decryption_time)
        # create an image from the cleartext and save it to its respective directory
        build_and_save(i, cleartext, 1)

        bar.update(t)
    print("\n\n")

    # output the results
    print_results(len(images), enc_times, dec_times)

if __name__ == '__main__':
    main()