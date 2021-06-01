from tkinter import *
from functools import partial
import time

# pip install pillow
from PIL import Image, ImageTk

# By default the image selected is thermal sensor
image_number = 0

# Set the desired image as the thermal sensor and display it asap 
def write_thermal(frame):
    global image_number
    
    # Set the image id to display as Thermal
    image_number = 0
    
    # Display image ASAP
    frame.after(0, write_image, frame)

# Set the desired image as the camera captured and display it asap     
def write_camera(frame):
    global image_number
    
    # Set the image id to display as camera
    image_number = 1
    
    # Display image ASAP
    frame.after(0, write_image, frame)
        
# This function shows the image which has been selected by the button
# The Image display is refressed every 250 ms 
def write_image(frame):
    global image_number
    
    try:
        if(image_number == 0):
            image = Image.open("thermalimage.jpg")
        else:
            image = Image.open("camimage.jpg")
    
        load = image. resize((450, 350), Image. ANTIALIAS)
        render = ImageTk.PhotoImage(load)
        img = Label(frame, image=render)
        img.image = render
        img.place(x=0, y=25)
    except:
        print("Image not found")
    
    # refress image after 250 ms
    frame.after(250, write_image, frame)

class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.pack(fill=BOTH, expand=1)
        
        # Create the Quit button
        quitButton = Button(self, text="Quit",
                            command=self.quit)
        # Place the button in cloumn 0 
        quitButton.grid(row = 0, column = 0, padx=10,pady=0)
        
        # create a button to show the Thermal Image
        ThermalButton = Button(self, text="Thermal",
                            command=partial(write_thermal, self))
        
        # Place the button in cloumn 1
        ThermalButton.grid(row = 0, column = 1, padx=10,pady=0)
        
        # Create a button to show the Camera Image
        cameraButton = Button(self, text="Camera",
                            command=partial(write_camera, self))
        
        # Place the button in cloumn 2
        cameraButton.grid(row = 0, column = 2, padx=10,pady=0)
        
        # call fn write_image()
        write_image(self)

# Create a Tkinter frame object      
root = Tk()

# Create class 
app = Window(root)
root.wm_title("Tkinter window")
root.geometry("450x350")
root.mainloop()