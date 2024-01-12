import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Socket Opened.")
server_address = ('127.0.0.1',5000)
client_socket.connect(server_address)
client_name = input("Client name: ")
print("Hello",client_name,"connection is being established...")
print("Connection established! say Hi!\n")

while (1):
    message = input("Client: ")
    if (message.lower() == "bye"):
        client_socket.send(message.encode())
        print("Client sent:", message)
        client_socket.close()
        print("Socket Closed.")
        break
    
    client_socket.send(message.encode())
    print("Client sent:", message)  
    data = client_socket.recv(1024)
    print("Client received:", data.decode())
    decodedvalue = data.decode()
    if (decodedvalue.lower() == "bye"):
        client_socket.close()
        print("Socket Closed.")
        break
    