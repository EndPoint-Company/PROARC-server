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
    'Database': 'testando1',
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

        # MOTIVO
        if action == "get_motivo":
            nome = request.get("nome")
            query = "SELECT nome FROM Motivos WHERE nome = ?"
            results = execute_query(query, (nome,))
            response = {"motivo": results[0] if results else None}
            print(response)

        elif action == "get_motivo_id":
            id = request.get("id")
            query = "SELECT nome FROM Motivos WHERE motivo_id = ?"
            results = execute_query(query, (id,))
            response = {"motivo": results[0] if results else None}
                             
        elif action == "get_id_motivo":
            nome = request.get("nome")
            query = "SELECT motivo_id FROM Motivos WHERE nome = ?"
            results = execute_query(query, (nome,))
            
            response = {"id": results[0] if results else None}
            print(response)

        elif action == "get_all_motivos":
            query = "SELECT nome FROM Motivos"
            results = execute_query(query)
            response = {"motivos": results}
            print(response)

        elif action == "add_motivo":
            motivo = request.get("motivo")
            query = "INSERT INTO Motivos (nome) VALUES (?)"
            execute_query(query, (motivo["Nome"], ))
            response = {"status": "success"}

        elif action == "remove_motivo":
            nome = request.get("nome")
            query = "DELETE FROM Motivos WHERE nome = ?"
            execute_query(query, (nome,))
            response = {"status": "success"}

        elif action == "update_motivo":
            nome = request.get("nome")
            novo_nome = request.get("novoNome")
            query = "UPDATE Motivos SET nome = ? WHERE nome = ?"
            execute_query(query, (novo_nome or nome, nome))
            response = {"status": "success"}
        # MOTIVO END
        # RECLAMADO
        elif action == "get_reclamado":
            nome = request.get("nome")
            query = "SELECT nome, cpf, cnpj, email, rua, bairro, cidade, uf FROM Reclamados WHERE nome = ?"
            results = execute_query(query, (nome,))
            response = {"reclamado": results[0] if results else None}
            print(response)

        elif action == "get_reclamado_id":
            id = request.get("id")
            query = "SELECT nome, cpf, cnpj, email, rua, bairro, cidade, uf FROM Reclamados WHERE reclamado_id = ?"
            results = execute_query(query, (id,))
            response = {"reclamado": results[0] if results else None}
        
        elif action == "get_all_reclamados":
            query = "SELECT nome, cpf, cnpj, email, rua, bairro, cidade, uf FROM Reclamados"
            results = execute_query(query)
            response = {"reclamados": results}
            print(response)

        elif action == "add_reclamado":
            reclamado = request.get("reclamado")
            query = "INSERT INTO Reclamados (nome, cpf, cnpj, email, rua, bairro, cidade, uf) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            execute_query(query, (reclamado["Nome"], reclamado["Cpf"], reclamado["Cnpj"], reclamado["Email"], reclamado["Rua"], reclamado["Bairro"], reclamado["Cidade"], reclamado["Uf"]))
            response = {"status": "success"}

        elif action == "remove_reclamado":
            nome = request.get("nome")
            query = "DELETE FROM Reclamados WHERE nome = ?"
            execute_query(query, (nome,))
            response = {"status": "success"}

        elif action == "update_reclamado":
            nome = request.get("nome")
            novo_nome = request.get("novoNome")
            query = "UPDATE Reclamados SET nome = ?, cpf = ?, cnpj = ?, email = ?, rua = ?, bairro = ?, cidade = ?, uf = ? WHERE nome = ?, cpf = ?, cnpj = ?, email = ?, rua = ?, bairro = ?, cidade = ?, uf = ?"
            execute_query(query, (novo_nome or nome, nome))
            response = {"status": "success"}
        # RECLAMADO END
        # RECLAMANTE
        

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
