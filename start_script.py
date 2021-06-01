import os 
from subprocess import run
from time import sleep

# Path and name to the script
capture_image_path = "python3 capture_image.py &"
temp_to_uno_mqtt_path = "python3 temp_to_uno_mqtt.py &"
gui_path = "python3 GUI.py &"

restart_timer = 2
def start_capture_image_script():
    try:
        # Make sure 'python' command is available
        os.system(capture_image_path)
    except:
        # If Script crashes, restart it
        handle_capture_image_crash()

def handle_capture_image_crash():
    sleep(restart_timer)  # Restarts the script after 2 seconds
    start_capture_image_script()

def start_temp_to_uno_mqtt_script():
    try:
        # Make sure 'python' command is available 
        os.system(temp_to_uno_mqtt_path)
    except:
        # If Script crashes, restart it
        handle_temp_to_uno_mqtt_crash()

def handle_temp_to_uno_mqtt_crash():
    sleep(restart_timer)  # Restarts the script after 2 seconds
    start_temp_to_uno_mqtt_script()
    
def start_gui_script():
    try:
        # Make sure 'python' command is available
        os.system(gui_path)
    except:
        # If Script crashes, restart it
        handle_gui_crash()

def handle_gui_crash():
    sleep(restart_timer)  # Restarts the script after 2 seconds
    start_gui_script()

start_capture_image_script()
start_temp_to_uno_mqtt_script()
start_gui_script()