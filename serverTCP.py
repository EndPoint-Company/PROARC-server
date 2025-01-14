import socket 
import threading 
import pyodbc as odbc

bind_ip = ""
bind_port = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.bind((bind_ip, bind_port)) 

server.listen() 

print(f"[+] Listening on port {bind_ip} : {bind_port}")                            

def handle_client(client_socket): 
    request = ''

    send_salt_to_client(client_socket)

    while True:
        msg = client_socket.recv(1024)
        if len(msg) <= 0:
            break
        request += msg.decode("utf-8")

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

def send_salt_to_client(client_socket):
    import pickle

    conn = odbc.connect('Driver={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.10.so.6.1};'
                        'Server=34.151.220.250;'
                        'Database=maconha2;'
                        'Trusted_Connection=no;'
                        'uid=sqlserver;'
                        'pwd=proarc;')
    
    cursor = conn.cursor()
    cursor.execute("SELECT salt FROM UsuariosTeste1")
    a = cursor.fetchall()

    print(a)

    data = pickle.dumps([tuple(row) for row in a])

    print(data)

    client_socket.send(data.encode("utf-8"))
    
    cursor.commit()

while True: 
    client, addr = server.accept() 
    print(f"[+] Accepted connection from: {addr[0]}:{addr[1]}")

    client_handler = threading.Thread(target=handle_client, args=(client,))
    client_handler.start() 
