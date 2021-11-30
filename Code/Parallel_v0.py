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
import threading
import random
import image_slicer
from image_slicer import join
import collections
from pathlib import Path
import shutil
import multiprocessing

#global path definitions
O_path = Path("Original_Images")
E_path = Path("Encrypted_Images")
D_path = Path("Decrypted_Images")
# img_dir = Path("Test")
img_dir = Path("SmallSet_Images")
# img_dir = Path("Sample_Images")


# Font for ImageDraw
myFont = Path("Fonts") / "Teletactile.ttf"

# Get the number of CPUs
# in the system using
# os.cpu_count() method
threadCount = os.cpu_count()
# threadCount = 2

exitFlag = 0

# initialize lists to hold execution times of encryption and decryption
enc_times = []
dec_times = []
#have thread list
threads = []
#have tile map (for keeping track of the shape and dimensions before encryption)
tilesMap = {}

#thread class
class encryptionThread (threading.Thread):
   def __init__(self, threadID, chunk, key, tile, encryptionMode):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.chunk = chunk
      self.key = key
      self.tile = tile
      self.encryptionMode = encryptionMode
   def run(self):
      if self.encryptionMode == 0: 
        # print ("Starting encryption on chunk " + str(self.threadID) + "\n")
        encrypt_chunk(self.chunk, self.key, self.tile)
        # print ("Finished encrypting chunk " + str(self.threadID) + "\n")
      else:
        # print ("Starting decryption on chunk " + str(self.threadID) + "\n")
        decrypt_chunk(self.chunk, self.key, self.tile)
        # print ("Finished decrypting chunk " + str(self.threadID) + "\n")
            

def create_image(cyphertext, tile, mode):
    if mode == 0:
        c_size = len(cyphertext)
        c_pixels = int((c_size+2)/3)
        W = H = int(math.ceil(c_pixels ** 0.5))

        data = cyphertext + b'\0' * (W*H*3 - len(cyphertext))
        cypherpic = Image.frombytes('RGB', (W, H), data)
        tile.image = cypherpic
    else:
        clearimage = Image.fromarray(np.frombuffer(cyphertext, dtype=tilesMap[tile.number].datatype).reshape(tilesMap[tile.number].shape))
        tile.image = clearimage

def encrypt_chunk(msg, key, tile):
    # get the cyphertext and the execution time from the encryption function
    cyphertext, encryption_time = encrypt(msg, key)
    # append the execution time to the respective list
    enc_times.append(encryption_time)
    #create the image and modify the tile
    create_image(cyphertext, tile, 0)

def decrypt_chunk(msg, key, tile):
    # get the cleartext (decrypted bytearray/text) and the execution time from the decryption function
    cleartext, decryption_time = decrypt(msg, key)
    # append the execution time to the respective list
    dec_times.append(decryption_time)
    #create the image and modify the tile
    create_image(cleartext, tile, 1)

# Wrapper for PIL images 
class Image_Data:
    def __init__(self, image, filename):
        self.image = image
        self.f_name = filename
        self.b_array = np.array(image).tobytes()
        self.shape = np.array(image).shape
        self.datatype = np.array(image).dtype.name

# Wrapper for PIL images 
class Tile_Data:
    def __init__(self, image, num):
        self.image = image
        self.b_array = np.array(image).tobytes()
        self.shape = np.array(image).shape
        self.datatype = np.array(image).dtype.name
        self.tileNumber = num

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
    im = image.convert('RGB')
    im.save(str(save_dir / filename))

# Create the images from the bytearray and save them to their respective directories for logging
def join_tiles_and_save(i_data, t_data, mode):
    if mode == 0: # encrypted image
        encrypted_image = join(t_data)
        label_and_save(encrypted_image, "Encrypted Image", i_data.f_name, E_path)
    elif mode == 1: #decrypted image
        decrypted_image = join(t_data)
        label_and_save(decrypted_image, "Decrypted Image", i_data.f_name, D_path)

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
    print("Average Encryption Time: "+str(round(np.mean(e_times), 4) * threadCount)+" seconds\n")
    print("Average Decryption Time: "+str(round(np.mean(d_times), 4) * threadCount)+" seconds\n")

# main driver code
def main():

    timerm = time.time()

    # Print the number of
    # CPUs in the system
    print("Thread count:", threadCount)

    # create images list
    images = get_images(img_dir)

    # if directories already exist, empty them, else create them
    setup_directories()

    # get the key
    k = get_key()

    # initialize a progress bar for loading images
    widgets = ['Batch Encryption/Decryption... ', progressbar.AnimatedMarker()]
    bar = progressbar.ProgressBar(widgets = widgets).start()
    t = 0

    # loop through loaded images and run encryption and decryption
    # timing information is gathered in the encrypt() and decrypt() functions
    for i in images:

        #slice up the image according to the number of cpu threads you have
        tiles = image_slicer.slice(i.image.filename, threadCount, save=False)

        t += 1

        # mark and save the input image to the respective directory
        label_and_save(i.image, "Original Image", i.f_name, O_path)

        for tile in tiles:
            #save tile data
            tilesMap[tile.number] = Tile_Data(tile.image, tile.number)
            # initialize message variable for input to encryption function (turn each tile into a byte array)
            msg = np.array(tile.image).tobytes()
            #create new thread & pass along the chunk with the key (mode = 0 for encryption)
            newThread = encryptionThread(tile.number, msg, k, tile, 0)
            newThread.start()
            threads.append(newThread)
        
        #wait for all of the threads to finish their work
        print("Waiting for all the threads to finish...")
        for thread in threads:
            thread.join()

        # join all of the tiles and save it to its respective directory (mode = 0 for encryption)
        join_tiles_and_save(i, tiles, 0)

        #start decryption process
        for tile in tiles:
            msg = np.array(tile.image).tobytes()

            # set mode to 1 for decryption
            threads[tile.number - 1] = encryptionThread(tile.number, msg, k, tile, 1)
            threads[tile.number - 1].start()

        print("Number of threads active: " + str(threading.active_count()))
        
        #wait for all of the threads to finish their work
        print("Waiting for all the threads to finish...")
        for thread in threads:
            thread.join()
        
        # join all of the tiles and save it to its respective directory (mode = 1 for decryption)
        join_tiles_and_save(i, tiles, 1)
        
        bar.update(t)
    print("\n\n")
    
    extime = round(time.time() - timerm, 4)
    print(f'overall time = {extime}')
    
    # output the results
    print_results(len(images), enc_times, dec_times)

if __name__ == '__main__':
    main()