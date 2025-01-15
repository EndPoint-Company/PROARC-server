import socket 
import threading 
import pyodbc as odbc

bind_ip = ""
bind_port = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.bind((bind_ip, bind_port)) 

server.listen() 

print(f"[+] Listening on port {bind_ip} : {bind_port}")                            

def handle_client_db_no_return(client_socket): 
    request = ''
    client_socket.settimeout(5)

    while True:
        try:
            msg = client_socket.recv(1024)
        except socket.timeout:
            break
        print(msg)
        if len(msg) <= 0:
            break
        request += msg.decode("utf-8")

    send_request_to_db(request)

    print(f"[*] Received: {request}")

    client_socket.close()


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
            if len(msg) <= 0:
                break
            #request += msg.decode("utf-8")
            request += msg.hex("-").upper()

        print(request)

        if (check_password(request)):
            client_socket.send("OK".encode("utf-8"))
            break
        client_socket.send("NOT OK".encode("utf-8")) 

    print(f"[*] Received: {request}")

    client_socket.close()


def send_request_to_db(request):
    conn = odbc.connect('Driver={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.10.so.6.1};'
                        'Server=34.151.220.250;'
                        'Database=maconha2;'
                        'Trusted_Connection=no;'
                        'uid=sqlserver;'
                        'pwd=proarc;')
    
    cursor = conn.cursor()
    cursor.execute(request)
    cursor.commit()

def check_password(hashed_password):
    conn = odbc.connect('Driver={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.10.so.6.1};'
                            'Server=34.151.220.250;'
                            'Database=maconha2;'
                            'Trusted_Connection=no;'
                            'uid=sqlserver;'
                            'pwd=proarc;')
        
    cursor = conn.cursor()
    cursor.execute("SELECT hash_and_salt FROM UsuariosTeste1")
    a = cursor.fetchall()

    for hash_and_salt in a:
        print("hash_and_salt: " + hash_and_salt[0])
        if hash_and_salt[0] == hashed_password:
            return True

    return False

def send_salt_to_client(client_socket):
    import json

    conn = odbc.connect('Driver={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.10.so.6.1};'
                        'Server=34.151.220.250;'
                        'Database=maconha2;'
                        'Trusted_Connection=no;'
                        'uid=sqlserver;'
                        'pwd=proarc;')
    
    cursor = conn.cursor()
    cursor.execute("SELECT salt FROM UsuariosTeste1")
    a = cursor.fetchall()

    data = json.dumps([tuple(row) for row in a])

    client_socket.send(data.encode("utf-8"))
    
    cursor.commit()

while True: 
    client, addr = server.accept() 
    print(f"[+] Accepted connection from: {addr[0]}:{addr[1]}")

    r = client.recv(8).decode("utf-8")

    if (r == "DBN"):
        client_handler = threading.Thread(target=handle_client_db_no_return, args=(client,))
        client_handler.start() 
    if (r == "DBR"):
        pass # TODO
    if (r == "AUTH"):
        client_handler = threading.Thread(target=handle_client_pwd, args=(client,))
        client_handler.start()
