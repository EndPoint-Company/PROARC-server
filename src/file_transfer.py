import socket
import os
from src.utils.colors import Colors as colors
from sys import platform

block_size = 1024

def handle_client_ftr(client_socket: socket.socket):
    try:
        client_socket.settimeout(1000)
      
        titulo = client_socket.recv(block_size).decode("utf-8").strip()
        arquivo = client_socket.recv(block_size).decode("utf-8").strip()
        if platform == "win32":
            file_path = os.path.join("tests", "home", "recl", titulo, arquivo)
        else:
            file_path = os.path.join(os.sep, "home", "~", "recl", titulo, arquivo)

        print(f"{colors.LIGHT_BLUE}[FT] file_path: {file_path}{colors.END}")

        if os.path.exists(file_path):
            with open(file_path, "rb") as file:
                print("data: ", end="")
                while (chunk := file.read(block_size)):
                    print(chunk, end="")
                    client_socket.send(chunk)
            print("[FT] File sent successfully.")

        else:
            print(f"{colors.LIGHT_RED}[FT] File not found: {file_path}{colors.END}")
            client_socket.send(b"ERROR: File not found.")

    except Exception as e:
        print(f"{colors.LIGHT_RED}[FT] Error in handle_client_ftr: {e}{colors.END}")

    finally:
        client_socket.close()

def handle_client_fts(client_socket: socket.socket):
        titulo = client_socket.recv(block_size).decode("utf-8").strip()
        arquivo = client_socket.recv(block_size).decode("utf-8").strip()
        if platform == "win32":
            file_path = os.path.join("tests", "home", "recl", titulo)
        else:
            file_path = os.path.join(os.sep, "home", "~", "recl", titulo)

        print(f"{colors.LIGHT_BLUE}[FT] file_path: {file_path}{colors.END}")

        if not os.path.exists(file_path):
            os.mkdir(file_path)

        try:
            client_socket.settimeout(1000)
            print("[+] Receiving file...")
            with open(os.path.join(file_path, arquivo), "wb") as file:
                    print("data: ", end="")
                    while True:
                        data = client_socket.recv(block_size)
                        print(data, end="")
                        if not data:
                            break
                        file.write(data)
                    print(f"{colors.LIGHT_GREEN}[FT] File received successfully.{colors.END}")     
        except Exception as e:
            print(f"{colors.LIGHT_RED}[FT] Error in handle_client_fts: {e}{colors.END}")

        finally:
            client_socket.close()
