import socket 
import threading 
import psycopg2
import global_config

bind_ip = ""
bind_port = 9999
block_size = 1024

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.bind((bind_ip, bind_port)) 

server.listen() 

print(f"[+] Listening on port {bind_port}")                            

def handle_client_db(client_socket): 
    import actions
    actions.handle_client(client_socket)

def handle_client_ftr(client_socket: socket.socket):
    import DwUp
    DwUp.handle_client_ftr(client_socket)

def handle_client_fts(client_socket: socket.socket):
    import DwUp
    DwUp.handle_client_fts(client_socket)

def handle_client_pwd(client_socket): 
    request = ''
    client_socket.settimeout(5)

    send_salt_to_client(client_socket)

    while True:
        while True:
            try:
                msg = client_socket.recv(1024)
            except socket.timeout:
                break
            print(msg)
            if len(msg) < 1024:
                request += msg.hex("-").upper()
                break
            if msg == b"BYE":
                break
            #request += msg.decode("utf-8")
            request += msg.hex("-").upper()

        print("request is: "+request)

        if (check_password(request)):
            print("OK")
            client_socket.send("OK".encode("utf-8"))
            break
        client_socket.send("NOT OK".encode("utf-8")) 
        request = ''

    print(f"[*] Received: {request}")

    client_socket.close()


def send_request_to_db(request):
    conn = psycopg2.connect(**global_config.db_config_pg)
    
    cursor = conn.cursor()
    cursor.execute(request)
    a = cursor.fetchall()

    conn.commit()
    cursor.close()
    conn.close()


def send_salt_to_client(client_socket):
    import json

    conn = psycopg2.connect(**global_config.db_config_pg)
     
    cursor = conn.cursor()
    cursor.execute("SELECT salt FROM Usuarios")
    a = cursor.fetchall()

    data = json.dumps([tuple(row) for row in a])

    client_socket.send(data.encode("utf-8"))
    
    conn.commit()
    cursor.close()
    conn.close()


def check_password(hashed_password):
    conn = psycopg2.connect(**global_config.db_config_pg)
        
    cursor = conn.cursor()
    cursor.execute("SELECT hash_and_salt FROM Usuarios")
    a = cursor.fetchall()

    for hash_and_salt in a:
        print("hash_and_salt: " + hash_and_salt[0] + " - " + hashed_password)
        if hash_and_salt[0] == hashed_password:
            return True

    return False


while True: 
    client, addr = server.accept() 
    print(f"[+] Accepted connection from: {addr[0]}:{addr[1]}")

    r = client.recv(8).decode("utf-8")

    if (r == "DB"):
        client_handler = threading.Thread(target=handle_client_db, args=(client,))
        client_handler.start() 

    if (r == "AUTH"):
        client_handler = threading.Thread(target=handle_client_pwd, args=(client,))
        client_handler.start()

    if (r == "FTR"):
        client_handler = threading.Thread(target=handle_client_ftr, args=(client,))
        client_handler.start()
    
    if (r == "FTS"):
        client_handler = threading.Thread(target=handle_client_fts, args=(client,))
        client_handler.start()
