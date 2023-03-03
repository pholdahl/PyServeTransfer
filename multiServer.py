import socket                               # Importing the socket module
import sys                                  # Importing the sys library, and using it for its exit() function
import os                                   # Importing the os library, and using several of its features to dynamicly create header metadata
import platform                             # Importing the platform library and using it to get server information for the header
import mimetypes                            # Importing the mimetypes library nad using it to get MIME type information for the header
import time                                 # Importing the time module
from charset_normalizer import detect       # Using the detect function form the charset_normaliser to detect the encoding format of requested file for the header
import threading                            # Import threading to handle multiple clients


HOST = socket.gethostname()                 # Set the host to localhost
PORT = 8080                                 # Setting the port number
MAX = 10                                    # Max number of clients at once

RESPCODES = {200: "OK", 404: "Not Found"}   # A dictionary containing responsecodes
                                                                                                

# clientHandler function to handle a client
def clientHandler(client):                                                                    # Clienthandler function that takes in the a connceting client
    try:
        incomingRequest = client.recv(2048).decode()                                                # Getting the request from the client
    except Exception as e:                                                                          # If receiving request throws an exception
        print(f"An error occurde while receiving request.")                                         # Print errormessage
        print(e)                                                                                    # Print the exception
        client.close()                                                                              # Close the client
        return                                                                                      # return
    
    incomingRequest = incomingRequest.split("\r\n")                                                 # Splitting the request at \n, to get a list of strings

    # Here I am splitting the incomingRequest message ex. GET http://host.com HTTP/1.1,
    # notice that the first variable requestMethod is not used later on in the code,
    # but I could have used it if I was going to build out this HTTP server so it also 
    # accepts POST, DELETE and so on. That would have required me to split up the clientHandler
    # into several different functions to handle the different requests,
    # and use the clientHandler primarly just for redirection.
    # But this is not required for the Oblig, so I will keep it simple.
    requestMethod, requestPath, requestProtocol = incomingRequest[0].split()                        

    if "http" in requestPath:                                                                       # If the address contains http, it will also contain //
        url = requestPath.split("/", 3)[3]                                                          # And the server i after the location, somewhere around .com/here
    else:                                                                                           
        url = requestPath.split("/", 1)[1]                                                          # Otherwise it does not contain //

    now = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.localtime())                              # Getting timestamp for date for the header
    serverInfo = f"{platform.system()}/{platform.release()} ({os.name})"                            # Getting server info for the header
    urlExists = os.path.exists(url)                                                                 # Checking if the file exists on the server
    if not urlExists:                                                                               # If it doesn't exist, create a 404 notFoundMessage
        notFoundMessage = \
f"""<!DOCTYPE html>                                                     
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>404 Not Found</title>
    </head>
    <body>
        <h1>404 Not Found</h1>
        <p>The requested URL {url} was not found on this server</p>
    </body>
</html>"""
        # Create a 404 notFoundHeader
        notFoundHeader = \
                            f"{requestProtocol} 404 {RESPCODES[404]}\r\n" \
                            f"Date: {now}\r\n" \
                            f"Server: {serverInfo}\r\n" \
                            f"Content-Length: {len(notFoundMessage)}\r\n" \
                            f"Content-Type: text/html; charset=utf-8\r\n" \
                            "Connection: close\r\n\r\n"
        notFound = notFoundHeader + notFoundMessage                                                 # Combining the messages
        try: 
            client.send(notFound.encode())                                                          # Sending to client
        except Exception as e:                                                                      # If sending to client throws an exception
            print(f"An error occurd while sending notFound message to client")                      # Print errormessage
            print(e)                                                                                # Print exception
            client.close()                                                                          # Close the client
            return                                                                                  # Return
        print(f"File not found, now closing client...")
    else:                                                                                           # Otherwise, if the file exists on the server
        content = None                                                                              # Content variable to store the data
        with open (url, 'rb') as file:                                                              # Trying to open the file and read as bytes
            content = file.read()                                                                   # Storing the data in the content variable
            charset = detect(content)['encoding']                                                   # Trying to detect the encoding of the file
        now = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.localtime())                          # Getting timestamp for date for the header
        serverInfo = f"{platform.system()}/{platform.release()} ({os.name})"                        # Getting server info for the header
        # Getting the last time modified for the file for the header:
        modified = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.strptime(str(time.ctime(os.path.getmtime('index.html')))))
        contentLength = len(content)                                                                # Checking the length of the content
        contentType = f"{mimetypes.guess_type(url)[0]}; charset={str(charset)}"                     # Checking the MIME type of the file
        # Create a 200 OK found header
        foundHeader = \
                        f"{requestProtocol} 200 {RESPCODES[200]}\r\n" \
                        f"Date: {now}\r\n" \
                        f"Server: {serverInfo}\r\n" \
                        f"Last-Modified: {modified}\r\n" \
                        f"Content-Length: {contentLength}\r\n" \
                        f"Content-Type: {contentType}\r\n" \
                        "Connection: close\r\n\r\n"
        try:
            client.send(foundHeader.encode())                                                       # Sending the header to the client
            for i in range(0, len(content)):                                                        # Sending the file to the client but not encoding
                client.send(content[i:i+1])                                                         # In the same way as in the skeleton code since its already a binary sequence
        except Exception as e:                                                                      # If sending to client throws an exception
            print(f"An error occurd while sending {url} to client")                                 # Print errormessage
            print(e)                                                                                # Print exception
            client.close()                                                                          # Close the client
            return                                                                                  # Return
        print(f"Delivered {url} successfully to client, now closing client...")                     # Print successmessage
    client.close()                                                                                  # Closing the client object
    return                                                                                          # Return

# serverHandler function to handle the server
def serverHandler():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                                      # Creating server object
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)                                    # Set option for the server socket such that the same address can be used on restart                           
    try:
        server.bind((HOST, PORT))                                                                   # Binding to a specific IP and Port number
        print(f"Python superserver is ready at {HOST} and port {PORT}")
    except Exception as e:                                                                          # If binding throws an exception
        print(f"Could not bind to {HOST} and port {PORT}")                                          # Print errormessage
        print(e)                                                                                    # Print exception
        server.close()                                                                              # Close the server
        return                                                                                      # Return
    
    server.listen(MAX)                                                                              # Listening for maximum number of clients

    while True:                                                                                     
        try: 
            client, addr = server.accept()                                                          # Accepting a client
        except Exception as e:                                                                      # If accepting client throws exception
            print("An error occurd while accepting a client")                                       # Print errormessage
            print(e)                                                                                # Print exception
            continue                                                                                # If Exception go back to start of while loop
        print(f"Client {addr} connected to server")                                                 # Printing a connect message
        threading.Thread(target=clientHandler, args=(client,)).start()                         # Starting the clientHandler on a new thread

# main function to start the server on a thread
def main():
    threading.Thread(target=serverHandler()).start()                                                # Starting the server on a thread
    sys.exit()                                                                                      # Exit script when return from server thread

# Standard python start command
if __name__ == "__main__":
    main()
