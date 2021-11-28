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
import random
import image_slicer
from image_slicer import join
import collections
from pathlib import Path
import shutil
import multiprocessing as mp

#global path definitions
O_path = Path("Original_Images")
E_path = Path("Encrypted_Images")
D_path = Path("Decrypted_Images")
img_dir = Path("Test")
# img_dir = Path("SmallSet_Images")
# img_dir = Path("Sample_Images")


# Font for ImageDraw
myFont = Path("Fonts") / "Teletactile.ttf"

exitFlag = 0

# initialize lists to hold execution times of encryption and decryption
enc_times = []
dec_times = []

# Wrapper for PIL images 
class Image_Data:
    def __init__(self, image, filename):
        self.image = image
        self.f_name = filename
        self.f_path = image.filename
        self.b_array = np.array(image).tobytes()
        self.shape = np.array(image).shape
        self.datatype = np.array(image).dtype.name

# Wrapper for Tile objects 
class Tile_Data:
    def __init__(self, tile):
        self.tile = tile
        self.image = tile.image
        self.b_array = np.array(tile.image).tobytes()
        self.shape = np.array(tile.image).shape
        self.datatype = np.array(tile.image).dtype.name
        self.tileNumber = tile.number
        self.cyphertext = b''
        self.cleartext = b''
    
    def set_cyphertext(self, text):
        self.cyphertext = text
    
    def set_cleartext(self, text):
        self.cleartext = text

def create_image(tile, mode):
    if mode == 0:
        cyphertext = tile.cyphertext
        c_size = len(cyphertext)
        c_pixels = int((c_size+2)/3)
        W = H = int(math.ceil(c_pixels ** 0.5))

        data = cyphertext + b'\0' * (W*H*3 - len(cyphertext))
        cypherpic = Image.frombytes('RGB', (W, H), data)
        return cypherpic
    if mode == 1:
        clearimage = Image.fromarray(np.frombuffer(tile.cleartext, dtype=tile.datatype).reshape(tile.shape))
        return clearimage

def make_tiles(image):
    tiles = []
    t_num = 0

    # slice up the image according to the number of cpu cores available
    for t in image_slicer.slice(image.f_path, mp.cpu_count(), save=False):
        tiles.append(Tile_Data(t))
        t_num += 1
    
    return tiles

# Encrypt plaintext and get execution time
def encrypt(message, F):
    timer1 = time.time()
    c_text = F.encrypt(message)
    extime = round(time.time() - timer1, 4)

    return [c_text, extime]

def encrypt_tile(tile, key):
    msg = tile.b_array

    result = encrypt(msg, key)

    tile.set_cyphertext(result[0])

    return result[1]

def encrypt_tiles(tiles, key):
    results=[]
    for t in tiles:
        results.append(encrypt_tile(t, key))

def parallel_encrypt(image, tiles, key):
    # run parallel encryption scheme using the number of processes = cpu count
    pool = mp.Pool(mp.cpu_count())
    #output = []

    results = pool.apply_async(encrypt_tile, (tiles, key))
    print ([r.get(timeout=1) for r in results])

    #results = output.get()
    pool.close()

    # build the image from encrypted tiles and save it (mode = 0 for handling encrypted tiles)
    # tile_images = [create_image(tile, mode=0) for tile in tiles]
    # join_tiles_and_save(image, tile_images, mode=0)

    # get the total execution time from all threads
    execution_time = sum(results)

    return execution_time

def parallel_decrypt(image, tiles, key):
    # run parallel encryption scheme using the number of processes = cpu count
    pool = mp.Pool(mp.cpu_count())
    #output = []
    results = pool.starmap_async(decrypt_tile, [(t, key) for t in tiles])
    #results = output.get()
    pool.close()

    # build the image from decrypted tiles and save it (mode = 1 for handling decrypted tiles)
    tile_images = [create_image(tile, mode=1) for tile in tiles]
    join_tiles_and_save(image, tile_images, mode=1)
    
    # get the total execution time from all threads
    execution_time = sum(results)

    return execution_time

def decrypt_tile(tile, key):
    msg = tile.cyphertext

    result = decrypt(msg, key)

    tile.set_cleartext(result[0])

    return result[1]

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
def join_tiles_and_save(i_data, t_data, mode):
    if mode == 0: # encrypted image
        encrypted_image = join(t_data)
        label_and_save(encrypted_image, "Encrypted Image", i_data.f_name, E_path)
    elif mode == 1: #decrypted image
        decrypted_image = join(t_data)
        label_and_save(decrypted_image, "Decrypted Image", i_data.f_name, D_path)

# Decrypt cyphertext and get execution time
def decrypt(cypher, F):
    timer2 = time.time()
    p_text = F.decrypt(cypher)
    extime = round(time.time() - timer2, 4)

    return [p_text, extime]

# print out the number of images used, and the average encryption and decryption times with a decimal precision of 4
def print_results(num_images, e_times, d_times):
    print("Number of images: "+str(num_images)+"\n")
    print("Average Encryption Time: "+str(round(np.mean(e_times), 4) * threadCount)+" seconds\n")
    print("Average Decryption Time: "+str(round(np.mean(d_times), 4) * threadCount)+" seconds\n")

# main driver code
def main():
    # get number of CPUs in system
    print("Thread count: {}".format(mp.cpu_count()))

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

        # progressbar iterator
        t += 1

        # mark and save the input image to the respective directory
        label_and_save(i.image, "Original Image", i.f_name, O_path)

        tiles = make_tiles(i)

        enc_times.append(parallel_encrypt(i, tiles, k))

        dec_times.append(parallel_decrypt(i, tiles, k))

        bar.update(t)
    print("\n\n")

    # output the results
    print_results(len(images), enc_times, dec_times)

if __name__ == '__main__':
    main()