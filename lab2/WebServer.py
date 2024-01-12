from socket import *

serverSocket = socket(AF_INET, SOCK_STREAM)

serverPort = 6789 
serverSocket.bind(('10.14.188.150', serverPort))
serverSocket.listen(1)

print('The server is ready to receive...')

while True:
    print('Ready to serve...')
    connectionSocket, addr = serverSocket.accept()

    try:
        message = connectionSocket.recv(1024).decode()
        filename = message.split()[1][1:] 

        try:
            with open(filename, 'rb') as file:
                outputdata = file.read()
            
            connectionSocket.send("HTTP/1.1 200 OK\r\n\r\n".encode())

            connectionSocket.sendall(outputdata)
        
        except FileNotFoundError:
            connectionSocket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())
            connectionSocket.send("404 Not Found".encode())

        connectionSocket.close()

    except Exception as e:
        print("Error:", e)

serverSocket.close()
