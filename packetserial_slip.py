import serial
import sliplib

""" 
END = 0300,
ESC = 0333,
ESC_END = 0334,
ESC_ESC = 0335 
"""


# Global settings of for the serial port
com_port = "/dev/ttyACM0"
baudrate = 1000000

#SLIP-Decoder
decoder = sliplib.Driver()

connection = serial.Serial(com_port, baudrate, timeout=0)
connection.flush()

#get the data from the serial-port
def data_in(expected_length):
    bytes_to_read = connection.inWaiting()
    
    if  bytes_to_read >= expected_length :
        byte_package = connection.read(expected_length)
        return byte_package
    
    else :
        return False
#get the Data form the Serial Device as List of bytes

def get_packages():
    packages = data_in(expected_length=20)
    if packages:
        return decoder.receive(packages)
    else: False
