import socket 
import threading 

bind_ip = "127.0.0.1" 
bind_port = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.bind((bind_ip, bind_port)) 

server.listen() 

print(f"[+] Listening on port {bind_ip} : {bind_port}")                            

def handle_client(client_socket): 
    request = ''

    while True:
        msg = client_socket.recv(1024)
        if len(msg) <= 0:
            break
        request += msg.decode("utf-8")

    print(f"[*] Received: {request}")
    client_socket.close()

while True: 
    client, addr = server.accept() 
    print(f"[+] Accepted connection from: {addr[0]}:{addr[1]}")

    client_handler = threading.Thread(target=handle_client, args=(client,))
    client_handler.start() 
