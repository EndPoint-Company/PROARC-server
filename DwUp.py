import socket
import threading
import os

bind_ip = "0.0.0.0"
bind_port = 9999
block_size = 1024

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip, bind_port))
server.listen()

print(f"[+] Listening on port {bind_ip}:{bind_port}")

def handle_client(client_socke:socket.socket):
    try:
        
        command = client_socket.recv(3).decode("utf-8")
        client_socket.settimeout(600000)

        if command == "FTS":  
            print("[+] Receiving file...")
            with open("received_file_from_client", "wb") as file:
                while True:
                    data = client_socket.recv(block_size)
                    if not data:
                        break
                    file.write(data)
            print("[+] File received successfully.")

        elif command == "FTR": 
            file_path = client_socket.recv(1024).decode("utf-8")
            if os.path.exists(file_path):
                print(f"[+] Sending file: {file_path}")
                with open(file_path, "rb") as file:
                    while (chunk := file.read(block_size)):

                        client_socket.send(chunk)
                print("[+] File sent successfully.")
            else:
                print(f"[-] File not found: {file_path}")
                client_socket.send(b"ERROR: File not found.")

        else:
            print(f"[-] Unknown command received: {command}")
    except Exception as e:
        print(f"[-] Error: {e}")
    finally:
        client_socket.close()


while True:
    client_socket, addr = server.accept()
    print(f"[+] Accepted connection from: {addr[0]}:{addr[1]}")

    client_handler = threading.Thread(target=handle_client, args=(client_socket,))
    client_handler.start()
