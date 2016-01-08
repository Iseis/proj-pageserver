"""
Socket programming in Python
  as an illustration of the basic mechanisms of a web server.

  Based largely on https://docs.python.org/3.4/howto/sockets.html
  This trivial implementation is not robust:  We have omitted decent
  error handling and many other things to keep the illustration as simple
  as possible. 

  FIXME:
  Currently this program always serves an ascii graphic of a cat.
  Change it to serve files if they end with .html and are in the current directory
"""

import socket    # Basic TCP/IP communication on the internet
import random    # To pick a port at random, giving us some chance to pick a port not in use
import _thread   # Response computation runs concurrently with main program 


def listen(portnum):
    """
    Create and listen to a server socket.
    Args:
       portnum: Integer in range 1024-65535; temporary use ports
           should be in range 49152-65535.
    Returns:
       A server socket, unless connection fails (e.g., because
       the port is already in use).
    """
    # Internet, streaming socket
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind to port and make accessible from anywhere that has our IP address
    serversocket.bind(('', portnum))
    serversocket.listen(1)    # A real server would have multiple listeners
    return serversocket

def serve(sock, func):
    """
    Respond to connections on sock.
    Args:
       sock:  A server socket, already listening on some port.
       func:  a function that takes a client socket and does something with it
    Returns: nothing
    Effects:
        For each connection, func is called on a client socket connected
        to the connected client, running concurrently in its own thread.
    """
    while True:
        print("Attempting to accept a connection on {}".format(sock))
        (clientsocket, address) = sock.accept()
        _thread.start_new_thread(func, (clientsocket,))


CAT = """
     ^ ^
   =(   )=
   """


def respond(sock):
    """
    Respond (only) to GET

    """
    sent = 0
    request = sock.recv(1024)  # We accept only short requests
    request = str(request, encoding='utf-8', errors='strict')
    print("\nRequest was {}\n".format(request))
    parts = request.split()

    #Check if we handle the request
    if len(parts) > 1 and parts[0] == "GET" and checkForValidFile(parts[1]):
       
        ## Get the file
        try:
            transmit("HTTP/1.0 200 OK\n\n".encode(), sock)
            file_handler = open(parts[1], 'rb')
            response = file_handler.read()
            file_handler.close()
            transmit(response, sock)
		
        except Exception as e: #in case file not found
            print("Error file not found sending 404 error\n", e)
            response = "HTTP/1.0  404 Not Found\n".encode()
            response += b"Error 404: File not found: Python HTTP server"
            transmit(response, sock)
			
    else:
        transmit("\nI don't handle this request: {}\n".format(request).encode(), sock)

    sock.close()

    return

def transmit(msg, sock):
    """It might take several sends to get the whole buffer out"""
    sock.send( msg )
    
#Checks if file part of url is valid
def checkForValidFile(f):
    isValid = False
    
    #if html file and is in same directory as server
    if '.html' in f:
       isValid = True
    
    #if css file and is in same directory as server
    if '.css' in f:
       isValid = True
    
    #Check for invalid characters in file name
    if '//' in f or '..' in f or '~' in f:
       isValid = False
       
    return isValid
       
    

def main():
    port = random.randint(5000,8000)
    sock = listen(port)
    print("Listening on port {}".format(port))
    print("Socket is {}".format(sock))
    serve(sock, respond)

main()
    
