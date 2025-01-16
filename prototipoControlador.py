import socket
import threading
import pyodbc
import json

bind_ip = "0.0.0.0"
bind_port = 6666

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip, bind_port))
server.listen()

print(f"[+] Listening on {bind_ip}:{bind_port}")

db_config = {
    'Driver': '{/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.10.so.6.1}',
    'Server': '34.151.220.250',
    'Database': 'maconha2',
    'Trusted_Connection': 'no',
    'uid': 'sqlserver',
    'pwd': 'proarc'
}

def execute_query(query, params=()):
    conn = pyodbc.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(query, params)
    if query.strip().lower().startswith("select"):
        results = cursor.fetchall()
        conn.close()
        return [tuple(row) for row in results]
    else:
        conn.commit()
        conn.close()
        return None

def handle_client(client_socket):
    try:
        data = client_socket.recv(4096).decode("utf-8").strip()
        request = json.loads(data)
        
        action = request.get("action")
        response = {}

        if action == "get_motivo":
            nome = request.get("nome")
            query = "SELECT nome, descricao FROM Motivos WHERE nome = ?"
            results = execute_query(query, (nome,))
            response = {"motivo": results[0] if results else None}
            print(response)

        elif action == "get_motivo_id":
            id = request.get("id")
            query = "SELECT nome, descricao FROM Motivos WHERE motivo_id = ?"
            results = execute_query(query, (id,))
            response = {"motivo": results[0] if results else None}
                             
        elif action == "get_id_motivo":
            nome = request.get("nome")
            query = "SELECT motivo_id FROM Motivos WHERE nome = ?"
            results = execute_query(query, (nome,))
            
            response = {"id": results[0] if results else None}
            print(response)

        elif action == "get_all_motivos":
            query = "SELECT nome, descricao FROM Motivos"
            results = execute_query(query)
            response = {"motivos": results}
            print(response)

        elif action == "add_motivo":
            motivo = request.get("motivo")
            query = "INSERT INTO Motivos (nome, descricao) VALUES (?, ?)"
            execute_query(query, (motivo["Nome"], motivo["Descricao"]))
            response = {"status": "success"}

        elif action == "remove_motivo":
            nome = request.get("nome")
            query = "DELETE FROM Motivos WHERE nome = ?"
            execute_query(query, (nome,))
            response = {"status": "success"}

        elif action == "update_motivo":
            nome = request.get("nome")
            novo_nome = request.get("novoNome")
            nova_descricao = request.get("novaDescricao")
            query = "UPDATE Motivos SET nome = ?, descricao = ? WHERE nome = ?"
            execute_query(query, (novo_nome or nome, nova_descricao or "", nome))
            response = {"status": "success"}

        client_socket.send(json.dumps(response).encode("utf-8"))
    except Exception as e:
        print(f"Error: {e}")
        client_socket.send(json.dumps({"error": str(e)}).encode("utf-8"))
    finally:
        client_socket.close()

while True:
    client, addr = server.accept()
    print(f"[+] Connection from: {addr}")
    client_handler = threading.Thread(target=handle_client, args=(client,))
    client_handler.start()
