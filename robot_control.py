import keyboard
import socket

# next create a socket object
s = socket.socket()
print("Socket successfully created")

# reserve a port on your computer in our
# case it is 12345 but it can be anything
port = 12345

# Next bind to the port
# we have not typed any ip in the ip field
# instead we have inputted an empty string
# this makes the server listen to requests
# coming from other computers on the network
s.bind(('', port))

# put the socket into listening mode
s.listen(1)

c, addr = s.accept()
print("Connected")

sent_s = False

while True:
    # send the arrow keys that are being pressed
    if keyboard.is_pressed("left arrow"):
        c.send("l".encode())
        sent_s = False
    if keyboard.is_pressed("right arrow"):
        c.send("r".encode())
        sent_s = False
    if keyboard.is_pressed("up arrow"):
        c.send("u".encode())
        sent_s = False
    if keyboard.is_pressed("down arrow"):
        c.send("d".encode())
        sent_s = False
    else:
        # if no arrow keys are clicked, send the stop signal
        if not sent_s:
            c.send("s".encode())
            sent_s = True
