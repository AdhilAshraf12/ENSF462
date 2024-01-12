import socket

server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
print("Socket Opened.")
server_address = ('127.0.0.1',5000)
server_socket.bind(server_address)

server_socket.listen(5)
print("Server is listening...")

client_socket, client_address = server_socket.accept()
print("Accepted connection from:", client_address)



while (1):
    data = client_socket.recv(1024)
    print("Server received:", data.decode())
    decodedvalue = data.decode()
    if (decodedvalue.lower() == "bye"):
        client_socket.close()
        server_socket.close()
        print("Socket Closed.")
        break

    response = input("Server: ")
    client_socket.send(response.encode())
    print("Server sent:", response)
    if (response.lower() == "bye"):
        client_socket.close()
        server_socket.close()
        print("Socket Closed.")
        break