import serial
import socket
import paho.mqtt.publish as publish

# Create an UDP socket 
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)      # For UDP
udp_host = "localhost" 		                                # Host IP
udp_port = 12345			                                # specified port to connect
sock.bind((udp_host,udp_port))                              # assign IP and port to the socket

# MQTT host address: use localhost
mqtt_host = "localhost"

if __name__ == '__main__':
    
    # Open a UART port on device                            # Rpi Pin 8 - Tx 
    # Port bitrate =  9600
    ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=1)
    ser.flush()
    while True:
        print("Waiting for temperature...")
        
        # Receive the temperature data from the camera on the UDP
        data,addr = sock.recvfrom(1024)	                    # Receive data from client
        
        # Convert to string from bitstream
        data = data.decode('utf-8')
        print("Received Messages:", data," from", addr)
        
        # Add a new line terminator for UNO to recieve
        msg = data + "\n"
        
        # Convert to bitstream 
        msg = msg.encode("utf-8")
        
        # Write the data out on the UART TX
        ser.write(msg)
        
        # Also publish the received temperature on MQTT broker hosted on the PRi
        # The data is posted on the topic "temperature"
        publish.single(topic = "temperature", payload = data, hostname = mqtt_host)