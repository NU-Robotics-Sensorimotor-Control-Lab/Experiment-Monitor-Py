import socket
import struct

# UDP_IP = "192.168.37.1"
UDP_IP = "165.124.9.239"
PORT = 5005


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

target_tor = 5
low_tor = 4
up_tor = 6
match_tor = 5.5

targetF = 7
lowF = 6
upF = 8
matchF = 6.45

sound_trigger = [False for i in range(13)]

stop_trigger = False

buf = bytes()

buf += struct.pack('<d', target_tor)
buf += struct.pack('<d', low_tor)
buf += struct.pack('<d', up_tor)
buf += struct.pack('<d', match_tor)

buf += struct.pack('<d', targetF)
buf += struct.pack('<d', lowF)
buf += struct.pack('<d', upF)
buf += struct.pack('<d', matchF)

for i in sound_trigger:
    buf += struct.pack('<?', i)

buf += struct.pack('<?', stop_trigger)

sock.sendto(buf, (UDP_IP, PORT))