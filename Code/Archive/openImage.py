import os, sys
from PIL import ImageTk
import PIL.Image 
import tkinter as tk  
from tkinter import * 
from tkinter import filedialog
from tkinter import simpledialog
import numpy as np

global img

len = 500
wid = 500

root = tk.Tk()

# getting screen's height in pixels 
height = root.winfo_screenheight() *.5
  
# getting screen's width in pixels 
width = root.winfo_screenwidth() * .5

#declare canvas of size 800 by 800
canvas = tk.Canvas(root, width = width, height = height)  
canvas.pack()  

#opening and post processing of image
def openImage():
   path =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
   print(path)
   startImage = PIL.Image.open(open(path, 'rb'))
   resize = startImage.resize((len, wid))

 
   #convert image into an array
   img_sequence = resize.getdata()
   image_array = np.array(img_sequence)
   #twoD = np.reshape(image_array, (len, wid))
   print(image_array)
   #save image and render it on the canvas
   img = ImageTk.PhotoImage(resize) 
   canvas.image = img #keep a reference
   canvas.create_image(0, 0, anchor=NW, image=img)

def changeDimensions():
   global len
   global wid

   len = simpledialog.askinteger("Input", "What is the height?",
                                parent=root)
   wid = simpledialog.askinteger("Input", "What is the width?",
                                parent=root)


B = tk.Button(root, text ="Open Image!", command = openImage)

B.pack()

newButton = tk.Button(root, text = "Change Image Dimensions", command = changeDimensions)

newButton.pack()

#run main gui loop
root.mainloop()
