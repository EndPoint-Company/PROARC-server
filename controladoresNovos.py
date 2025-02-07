import datetime
import socket
import pyodbc
import json
import global_config

def execute_query(query, params=()):
    conn = pyodbc.connect(**global_config.get_db_config())
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

action_handlers = {}

def action_insert_reclamacao(request):
    # todo o negocio que ambas tem em comum
    if processo["datadeaudicne"] in processo:
        # todo o negocio de reclamacao geral
        pass
    if processo["observacao"] in processo:
        # todo o negocio de reclamacao enel
        pass

def handle_client(client_socket):
    client_socket.settimeout(20)

    try:
        data = client_socket.recv(4096).decode("utf-8").strip()
        request = json.loads(data)
        action = request.get("action")
        
        if action in action_handlers:
            response = action_handlers[action](request)
        else:
            response = {"status": "unknown action"}

        client_socket.send(json.dumps(response).encode("utf-8"))
    except Exception as e:
        print(f"Error: {e}")
        client_socket.send(json.dumps({"error": str(e)}).encode("utf-8"))
    finally:
        client_socket.close()