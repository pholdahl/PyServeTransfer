import socket                              # Importing the socket library
import sys                                 # Importing the sys library
import os                                  # Importing the os library

 # Constants like size, or messages
SIZE = 2048
INPUTERROR = ("You seem to have some kind of typo in either server or port,"
            "please input server address and port number again.")
CONNECTERROR = "Something went wrong while connecting try again later."
SENDERROR = "Something went wrong while sending the request."
RECVERROR = "Something went wrong while receiving from server."
IMGERROR = "Something went wrong while storing the image from the server."


def main():
    # If Task 2 did not explicitly tell me that the input command format should be:
    # client.py server_host server_port filename
    # I would have added the possiblity to also input other HTTP methods.
    # The result is that the GET method is hardcoded.
    
    # To run multiTester.py, comment the three lines with sys.argv, and uncomment the host, port and file variables.

    host = sys.argv[1]                                                                  # Storing the server_host portion from terminal in host
    port = sys.argv[2]                                                                  # Storing the server_port portion from terminal in port
    file = sys.argv[3]                                                                  # Storing the filename in file

    # Variables used for testing
    # host = "127.0.0.1"
    # port = "8080"
    # file = "index.html"

    imgExtensions = ["apng", "avif", "gif", "jpg", "jpeg", "jfif",                      # A list of image extentions, so we can GET images
                    "pjpeg", "pjp", "img", "png", "svg", "webp"]

    while True:                                                                         # Checking if the console inputs seems ok
        inputOK = True
        if "www" not in host or "http" not in host:
            if not any(char.isdigit() for char in host):
                inputOK = False
        if not any(char.isdigit() for char in port):
            inputOK = False
        if inputOK == False:                                                            # Getting new input something wrong was detected
            print(INPUTERROR)
            host = sys.stdin.readline().strip("\n")
            port = sys.stdin.readline().strip("\n")
            continue
        elif inputOK == True:                                                           # If nothing seems wrong, we break
            break

    while True:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                      # Creating client object
        try:
            client.connect((host, int(port)))                                           # Trying to connect to the HTTP server
        except Exception:                                                               # If an exception occurs
            print(CONNECTERROR)                                                         # Print connect error message
            client.close()                                                              # closing clientobject
            return                                                                      # Exiting script

        # Creating requestMessage
        requestMessage = \
                            f"GET /{file} HTTP/1.1\r\n"\
                            f"Host: {host}:{port}\r\n"\
                            f"Connection: close\r\n\r\n"
        try:
            client.send(requestMessage.encode())                                        # Sending requestMessage
        except Exception:
            print(SENDERROR)
            client.close()
            return

        # Checking if requested file is an image
        isImage = False                                                                 
        img = ""                                                                        # Storing image name in img variable
        ext = ""                                                                        # Storing image extension in ext variable
        if "." in file:
            img, ext = file.split(".")
            for getExt in imgExtensions:
                if ext == getExt:
                    isImage = True
                    break

        response = b""                                                                  # Getting the response
        
        while True:
            try:
                data = client.recv(SIZE)                                                # Not decoding, in case it is an imaga
                if not data:
                    break
                response += data
            except Exception:
                print(RECVERROR)
                client.close()
                return


        header, message = response.split(b"\r\n\r\n")                                   # Splitting the response
        header = header.decode()                                                        # Decoding the header
        header += "\r\n\r\n"                                                            # Re-adding the two newlines to the header

        print(header)                                                                   # Printing the header

        if isImage:                                                                     # If the message is an imaga
            
            # Figuring out if the image is already stored locally, if so change filename to filename with number
            filename = file                                                              
            counter = 1
            while os.path.exists(filename):
                filename = f"{img}({counter}).{ext}"
                counter += 1

            print((f"Received {len(message)} bytes of data for an image. "              # Printing some information about the image
                    f"Storing the image as {filename}"))
            
            try:
                with open(filename, "wb") as img:                                       # Trying to store the image on disk
                    img.write(message)                                                      
            except Exception:
                print(IMGERROR)
                client.close()
                return
        else:                                                                            # Otherwise
            print(message.decode())                                                      # Decode and print the message

        print("Exiting client...")
        client.close()                                                                  # Closing client
        return                                                                          # Exiting script

# Standard python starting command
if __name__ == "__main__":
    main()
    sys.exit()