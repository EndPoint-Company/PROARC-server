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

    while True:
        msg = client_socket.recv(1024)
        if len(msg) <= 0:
            break
        request += msg.decode("utf-8")

    print(f"[*] Received: {request}")
    
    conn = odbc.connect('Driver={SQL Server};'
                        'Server=34.151.220.250;'
                        'Database=maconha2;'
                        'Trusted_Connection=no;'
                        'uid=sqlserver;'
                        'pwd=proarc;')
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM maconha2.dbo.TESTE")
    a = cursor.fetchall()
    for resultado in a:
        print(resultado)
    cursor.commit()
    
    client_socket.close()

while True: 
    client, addr = server.accept() 
    print(f"[+] Accepted connection from: {addr[0]}:{addr[1]}")

    client_handler = threading.Thread(target=handle_client, args=(client,))
    client_handler.start() 
