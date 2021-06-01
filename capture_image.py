import os
import math
import time
import numpy as np
import pygame

from PIL import Image
from scipy.interpolate import griddata
from colour import Color
from picamera import PiCamera

import socket
import schedule
import busio
import board
import adafruit_amg88xx

# Inilialize the RPi I2C bus
i2c_bus = busio.I2C(board.SCL, board.SDA)

# Initialize the Pi Camera
camera = PiCamera()

# Low temp range of the sensor (Blue range)
MINTEMP = 26.0

# High temp range of the sensor (Red range)
MAXTEMP = 40.0

# Color value depth range 
COLORDEPTH = 1024
os.putenv("SDL_FBDEV", "/dev/fb1")

# Initialize all imported pygame modules to creat the UI
pygame.init()

# Initialize the thermal sensor
sensor = adafruit_amg88xx.AMG88XX(i2c_bus)

# Initialize 8x8 point array
points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0, 64)]

# Create a 2 dimentional “meshgrid” with 0 to 7 with 32 intervals
grid_x, grid_y = np.mgrid[0:7:32j, 0:7:32j]

# Size of display for an 8x8 grid
height = 240
width = 240

# The list of colors we can choose from
blue = Color("indigo")
colors = list(blue.range_to(Color("red"), COLORDEPTH))

# Creating the array of colors
colors = [(int(c.red * 255), int(c.green * 255), int(c.blue * 255)) for c in colors]

# Dispaly width/height of each pixel of the image image on the UI
displayPixelWidth = width / 30
displayPixelHeight = height / 30

# Initializing the display surface of the pygame
lcd = pygame.display.set_mode((width, height))

# Initialing RGB Color (Red)
lcd.fill((255, 0, 0))

# Updating the display 
pygame.display.update()
pygame.mouse.set_visible(False)

# Set the display to black
lcd.fill((0, 0, 0))
pygame.display.update()

# Some utility functions
def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

# Map the value from input to output ranges
def map_value(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

# Let the sensor initialize
time.sleep(0.1)

# Create an array of zeros
array = np.zeros([height, width, 3], dtype=np.uint8)

# Create an UDP socket
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)      # For UDP

# UDP host IP
udp_host = "localhost" 		                                # Host IP

# UDP port
udp_port = 12345			        # specified port to connect
print( "UDP target IP:", udp_host)
print( "UDP target Port:", udp_port)

def create_temp_to_image(s):

    # Reads the pixels from the sensor &
    # extract the max temp value
    msg1 = str(np.amax(sensor.pixels))
    
    try:
        # Publish the max temperature on the UDP socket
        s.sendto(msg1.encode('utf-8'),(udp_host,udp_port))  # Sending message to UDP server
    except Exception as error:
        print(error)
        print("socket send failed")
        pass

    print(msg1)
    pixels = []
    
    # Map the temperature to the colour values
    for row in sensor.pixels:
        pixels = pixels + row
    pixels = [map_value(p, MINTEMP, MAXTEMP, 0, COLORDEPTH - 1) for p in pixels]

    # Perform interpolation
    bicubic = griddata(points, pixels, (grid_x, grid_y), method = "cubic")

    # Draw everything
    for ix, row in enumerate(bicubic):
        for jx, pixel in enumerate(row):
            array[int(displayPixelWidth * jx): int(displayPixelWidth * (jx+1)), int(displayPixelHeight * ix): int(displayPixelHeight * (ix+1))]= colors[constrain(int(pixel), 0, COLORDEPTH - 1)]
            
            # Draw the pixels within the display area for the temperature
            pygame.draw.rect(
                lcd,
                colors[constrain(int(pixel), 0, COLORDEPTH - 1)],
                (
                    displayPixelHeight * ix,
                    displayPixelWidth * jx,
                    displayPixelHeight,
                    displayPixelWidth,
                ),)
    # Create an image from the array
    img = Image.fromarray(array)
    try:
        # Save the image onto a file
        img.save('thermalimage.jpg')
    except:
        print("unable to write. Try later")

    # Update the pygame display to refresh the captured image
    pygame.display.update()

# Function to capture the camera image and store it as an image file
def capture_cam_image():
    camera.capture("camimage.jpg")
    
# Schedule the create_temp_to_image() func every second
schedule.every(1).seconds.do(create_temp_to_image,sock)

# schedule the capture_cam_image() func every second
schedule.every(1).seconds.do(capture_cam_image)

# run the scheduler
while True:
    schedule.run_pending()
    time.sleep(1)