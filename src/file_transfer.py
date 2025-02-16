import socket
import os

block_size = 1024

def handle_client_ftr(client_socket: socket.socket):
    try:
        client_socket.settimeout(1000)
      
        titulo = client_socket.recv(block_size).decode("utf-8").strip()
        arquivo = client_socket.recv(block_size).decode("utf-8").strip()
        file_path = os.path.join(os.sep, "home", "~", "recl", titulo, arquivo)

        if os.path.exists(file_path):
            print(f"[+] Sending file: {file_path}")
            with open(file_path, "rb") as file:
                while (chunk := file.read(block_size)):
                    client_socket.send(chunk)
            print("[+] File sent successfully.")

        else:
            print(f"[-] File not found: {file_path}")
            client_socket.send(b"ERROR: File not found.")

    except Exception as e:
        print(f"[-] Error in handle_client_ftr: {e}")

    finally:
        client_socket.close()

def handle_client_fts(client_socket: socket.socket):
        titulo = client_socket.recv(block_size).decode("utf-8").strip()
        arquivo = client_socket.recv(block_size).decode("utf-8").strip()
        file_path = os.path.join(os.sep, "home", "~", "recl", titulo)

        if not os.path.exists(file_path):
             os.mkdir(file_path)

        try:
            client_socket.settimeout(1000)
            print("[+] Receiving file...")
            with open(os.path.join(file_path, arquivo), "wb") as file:
                    while True:
                        data = client_socket.recv(block_size)
                        if not data:
                            break
                        file.write(data)
                    print("[+] File received successfully.")     
        except Exception as e:
            print(f"[-] Error in handle_client_ftr: {e}")

        finally:
            client_socket.close()
