from socket import *
import sys
import os
import http.client
import threading

BUFFER_SIZE = 4096

def handle_client(tcpCliSock):
    message = tcpCliSock.recv(1024).decode()
    print(message)

                                                                                # Extract the filename from the given message
    filename = message.split()[1].partition("/")[2]
    print(filename)
    fileExist = os.path.isfile(filename)                                        # Check if the file exists in the cache

    if fileExist:
                                                                                # Object found in cache, serve it to the client
        with open(filename, 'rb') as cache_file:
            response_data = cache_file.read()
        tcpCliSock.send("HTTP/1.0 200 OK\r\n".encode())
        tcpCliSock.send("Content-Type: application/octet-stream\r\n".encode())
        tcpCliSock.send("Connection: close\r\n\r\n".encode())
        tcpCliSock.sendall(response_data)
        print('Read from cache')

    else:
                                                                                # Check if it's a GET request
        if not message.startswith('GET'):
                                                                                # Invalid request, send "400 Bad Request" response
            tcpCliSock.send("HTTP/1.0 400 Bad Request\r\n".encode())
            tcpCliSock.send("Connection: close\r\n\r\n".encode())
        else:
                                                                                # Extract hostname and path from the request
            host_start = message.find("Host:") + 6
            host_end = message.find("\r\n", host_start)
            hostname = message[host_start:host_end].strip()

                                                                                # Create a connection to the actual host
            try:
                conn = http.client.HTTPSConnection(hostname)                    # Use HTTPS connection (you can use HTTP if the server does not support HTTPS)
                path = message.split()[1]
                conn.request("GET", path)                                       # Send the request to the actual host
                response = conn.getresponse()

                                                                                # Read the response data
                response_data = response.read()

                                                                                # Cache the response
                with open(filename, 'wb') as cache_file:
                    cache_file.write(response_data)

                                                                                # Send the response to the client
                tcpCliSock.send("HTTP/1.0 200 OK\r\n".encode())
                tcpCliSock.send("Content-Type: application/octet-stream\r\n".encode())
                tcpCliSock.send("Connection: close\r\n\r\n".encode())
                tcpCliSock.sendall(response_data)
                conn.close()

            except Exception as e:
                print("Error: ", e)
                                                                                # Send "400 Bad Request" response to the client for errors
                tcpCliSock.send("HTTP/1.0 400 Bad Request\r\n".encode())
                tcpCliSock.send("Connection: close\r\n\r\n".encode())

                                                                                # Close the client socket
        tcpCliSock.close()

if len(sys.argv) <= 1:
    print('Usage : "python ProxyServer.py server_ip"\n[server_ip : It is the IP Address Of Proxy Server')
    sys.exit(2)

tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.bind(('localhost', 8888))                                            # Bind to localhost and port 8888
tcpSerSock.listen(5)                                                            # Maximum 5 queued connections

print('Proxy server listening on port 8888...')

while True:
    print('Ready to serve...')
    tcpCliSock, addr = tcpSerSock.accept()
    print('Received a connection from:', addr)

                                                                                # Create a new thread to handle the client request
    client_handler = threading.Thread(target=handle_client, args=(tcpCliSock,))
    client_handler.start()

                                                                                # Close the server socket
tcpSerSock.close()
