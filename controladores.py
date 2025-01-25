import socket
import pyodbc
import json

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
        if action == "get_motivo_by_nome":
            nome = request.get("nome")
            query = "SELECT nome FROM Motivos WHERE nome = ?"
            results = execute_query(query, (nome,))
            response = {"motivo": results[0] if results else None}

        elif action == "get_motivo_by_id":
            id = request.get("id")
            query = "SELECT nome FROM Motivos WHERE motivo_id = ?"
            results = execute_query(query, (id,))
            response = {"motivo": results[0] if results else None}
            print(response)
                             
        elif action == "get_id_motivo_by_nome":
            nome = request.get("nome")
            query = "SELECT motivo_id FROM Motivos WHERE nome = ?"
            results = execute_query(query, (nome,))            
            response = {"id": results[0] if results else None}

        elif action == "get_all_motivos":
            query = "SELECT nome FROM Motivos"
            results = execute_query(query)
            response = {"motivos": results}

        elif action == "add_motivo":
            motivo = request.get("motivo")
            query = "INSERT INTO Motivos (nome) VALUES (?)"
            execute_query(query, (motivo["Nome"],))
            response = {"status": "success"}

        elif action == "remove_motivo_by_nome":
            nome = request.get("nome")
            query = "DELETE FROM Motivos WHERE nome = ?"
            execute_query(query, (nome,))
            response = {"status": "success"}

        elif action == "update_motivo_by_id":
            nome = request.get("nome")
            novo_nome = request.get("novoNome")
            query = "UPDATE Motivos SET nome = ? WHERE nome = ?"
            execute_query(query, (novo_nome or nome, nome))
            response = {"status": "success"}

        elif action == "count_motivos":
            query = "SELECT COUNT(*) FROM Motivos"
            results = execute_query(query)
            response = {"count": results[0][0]}

        # RECLAMADO
        elif action == "get_reclamado_by_id":
            id = request.get("id")
            query = """
                SELECT nome, cpf, cnpj, numero_rua, email, rua, bairro, cidade, uf 
                FROM Reclamados WHERE reclamado_id = ?
            """
            results = execute_query(query, (id,))
            response = {"reclamado": results[0] if results else None}

        elif action == "add_reclamado":
            reclamado = request.get("reclamado")
            query = """
                INSERT INTO Reclamados (nome, cpf, cnpj, numero_rua, email, rua, bairro, cidade, uf)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            execute_query(query, (
                reclamado["Nome"], reclamado["Cpf"], reclamado["Cnpj"],
                reclamado["NumeroRua"], reclamado["Email"], reclamado["Rua"],
                reclamado["Bairro"], reclamado["Cidade"], reclamado["Estado"]
            ))
            response = {"status": "success"}

        elif action == "update_reclamado_by_id":
            id = request.get("id")
            reclamado = request.get("reclamado")
            query = """
                UPDATE Reclamados
                SET nome = ?, cpf = ?, cnpj = ?, numero_rua = ?, email = ?, rua = ?, bairro = ?, cidade = ?, uf = ?
                WHERE reclamado_id = ?
            """
            execute_query(query, (
                reclamado["Nome"], reclamado["Cpf"], reclamado["Cnpj"],
                reclamado["NumeroRua"], reclamado["Email"], reclamado["Rua"],
                reclamado["Bairro"], reclamado["Cidade"], reclamado["Estado"], id
            ))
            response = {"status": "success"}

        elif action == "remove_reclamado_by_id":
            id = request.get("id")
            query = "DELETE FROM Reclamados WHERE reclamado_id = ?"
            execute_query(query, (id,))
            response = {"status": "success"}

        elif action == "get_all_reclamados":
            query = """
                SELECT reclamado_id, nome, cpf, cnpj, numero_rua, email, rua, bairro, cidade, uf 
                FROM Reclamados
            """
            results = execute_query(query)
            response = {"reclamados": results}

        elif action == "count_reclamados":
            query = "SELECT COUNT(*) FROM Reclamados"
            results = execute_query(query)
            response = {"count": results[0][0]}

        # RECLAMANTE
        elif action == "get_reclamante_by_id":
            id = request.get("id")
            query = """
                SELECT reclamante_id, nome, rg, cpf FROM Reclamantes WHERE reclamante_id = ?
            """
            results = execute_query(query, (id,))
            response = {"reclamante": results[0] if results else None}
            print(response)

        elif action == "get_reclamante_by_cpf":
            cpf = request.get("cpf")
            query = "SELECT reclamante_id, nome, rg, cpf FROM Reclamantes WHERE cpf = ?"
            results = execute_query(query, (cpf,))
            response = {"reclamante": results[0] if results else None}

        elif action == "get_reclamante_by_rg":
            rg = request.get("rg")
            query = "SELECT reclamante_id, nome, rg, cpf FROM Reclamantes WHERE rg = ?"
            results = execute_query(query, (rg,))
            response = {"reclamante": results[0] if results else None}

        elif action == "get_all_reclamantes":
            query = """
                SELECT reclamante_id, nome, rg, cpf FROM Reclamantes
            """
            results = execute_query(query)
            response = {"reclamantes": results}

        elif action == "add_reclamante":
            reclamante = request.get("reclamante")
            query = """
                INSERT INTO Reclamantes (nome, rg, cpf)
                VALUES (?, ?, ?)
            """
            execute_query(query, (reclamante["Nome"], reclamante["Rg"], reclamante["Cpf"]))
            response = {"status": "success"}

        elif action == "update_reclamante_by_id":
            id = request.get("id")
            reclamante = request.get("reclamante")
            query = """
                UPDATE Reclamantes
                SET nome = ?, rg = ?, cpf = ?
                WHERE reclamante_id = ?
            """
            execute_query(query, (reclamante["Nome"], reclamante["Rg"], reclamante["Cpf"], id))
            response = {"status": "success"}
        
        elif action == "remove_reclamante_by_id":
            id = request.get("id")
            query = "DELETE FROM Reclamantes WHERE reclamante_id = ?"
            execute_query(query, (id,))
            response = {"status": "success"}

        elif action == "count_reclamantes":
            query = "SELECT COUNT(*) FROM Reclamantes"
            results = execute_query(query)
            response = {"count": results[0][0]}

        # PROCESSO
        elif action == "get_processo_by_id":
            id = request.get("id")
            query = """
                SELECT processo_id, motivo_id, reclamante_id, titulo_processo, status_processo, path_processo, ano, data_audiencia 
                FROM ProcessosAdministrativos WHERE processo_id = ?
            """
            results = execute_query(query, (id,))
            results = json.dumps(results, default=str)
            response = {"processo": results}    
            print(response)     

        elif action == "get_processos_by_status":
            status = request.get("status")
            query = "SELECT processo_id, motivo_id, reclamante_id, titulo_processo, status_processo, path_processo, ano, data_audiencia FROM ProcessosAdministrativos WHERE status_processo = ?"
            results = execute_query(query, (status,))
            response = {"processos": results}

        elif action == "get_processos_by_reclamante_id":
            reclamante_id = request.get("reclamante_id")
            query = """
                SELECT processo_id, motivo_id, titulo_processo, status_processo, path_processo, ano, data_audiencia 
                FROM ProcessosAdministrativos 
                WHERE reclamante_id = ?
            """
            results = execute_query(query, (reclamante_id,))
            response = {"processos": results}

        elif action == "get_processos_by_motivo_id":
            motivo_id = request.get("motivo_id")
            query = """
                SELECT processo_id, motivo_id, titulo_processo, status_processo, path_processo, ano, data_audiencia 
                FROM ProcessosAdministrativos 
                WHERE motivo_id = ?
            """
            results = execute_query(query, (motivo_id,))
            response = {"processos": results}


        elif action == "get_all_processos":
            query = """
                SELECT processo_id, motivo_id, reclamante_id, titulo_processo, status_processo, path_processo, ano, data_audiencia 
                FROM ProcessosAdministrativos
            """
            results = execute_query(query)
            results = json.dumps(results, default=str)
            response = {"processos": results}
            print(response)

        elif action == "add_processo":
            processo_id = request.get("processo_id")
            motivo_id = request.get("motivo_id")
            reclamante_id = request.get("reclamante_id")
            titulo_processo = request.get("titulo_processo")
            ano = request.get("ano")
            status_processo = request.get("status_processo")
            path_processo = request.get("path_processo")
            data_audiencia = request.get("data_audiencia")

            query = "INSERT INTO ProcessosAdministrativos (processo_id, motivo_id, reclamante_id, titulo_processo, status_processo, path_processo, ano, data_audiencia) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            execute_query(query, (processo_id, motivo_id, reclamante_id, titulo_processo, status_processo, path_processo, ano, data_audiencia))
            response = {"status": "success"}

        elif action == "update_processo_by_id":
            id = request.get("id")

            motivo_id = request.get("motivo_id")
            reclamante_id = request.get("reclamante_id")
            titulo_processo = request.get("titulo_processo")
            ano = request.get("ano")
            status_processo = request.get("status_processo")
            path_processo = request.get("path_processo")
            data_audiencia = request.get("data_audiencia")

            query = "UPDATE ProcessosAdministrativos SET processo_id = ?, motivo_id = ?, reclamante_id = ?, titulo_processo = ?, status_processo = ?, path_processo = ?, ano = ?, data_audiencia = ? WHERE processo_id = ?"
            execute_query(query, (id, motivo_id, reclamante_id, titulo_processo, status_processo, path_processo, ano, data_audiencia, id))
            response = {"status": "success"}


        elif action == "remove_processo_by_id":
            id = request.get("id")
            query = "DELETE FROM ProcessosAdministrativos WHERE processo_id = ?"
            execute_query(query, (id,))
            response = {"status": "success"}

        elif action == "count_processos":
            query = "SELECT COUNT(*) FROM ProcessosAdministrativos"
            results = execute_query(query)
            response = {"count": results[0][0]}

        # RELACAO
        elif action == "add_relacao_processo_reclamado":
            processo_id = request.get("processo_id")
            reclamado_id = request.get("reclamado_id")
            query = """
                INSERT INTO RelacaoProcessoReclamado (processo_id, reclamado_id)
                VALUES (?, ?)
            """
            execute_query(query, (processo_id, reclamado_id))
            response = {"status": "success"}

        elif action == "remove_relacao_processo_reclamado":
            processo_id = request.get("processo_id")
            reclamado_id = request.get("reclamado_id")
            query = """
                DELETE FROM RelacaoProcessoReclamado 
                WHERE processo_id = ? AND reclamado_id = ?
            """
            execute_query(query, (processo_id, reclamado_id))
            response = {"status": "success"}

        elif action == "get_reclamado_from_relacao_by_processo_id":
            processo_id = request.get("processo_id")
            query = """
                SELECT reclamado_id 
                FROM RelacaoProcessoReclamado 
                WHERE processo_id = ?
            """
            results = execute_query(query, (processo_id,))
            response = {"reclamados": results}

        elif action == "get_processo_from_relacao_by_reclamado_id":
            reclamado_id = request.get("reclamado_id")
            query = """
                SELECT processo_id 
                FROM RelacaoProcessoReclamado 
                WHERE reclamado_id = ?
            """
            results = execute_query(query, (reclamado_id,))
            response = {"processos": results}

        elif action == "get_all_relacao_processo_reclamado":
            query = """
                SELECT processo_id, reclamado_id 
                FROM RelacaoProcessoReclamado
            """
            results = execute_query(query)
            response = {"relacao": results}

        # HISTORICO
        elif action == "add_historico_mudanca_status":
            processo_id = request.get("processo_id")
            status_old = request.get("status_old")
            status_new = request.get("status_new")
            query = """
                INSERT INTO HistoricoMudancaStatus (processo_id, status_old, status_new)
                VALUES (?, ?, ?)
            """
            execute_query(query, (processo_id, status_old, status_new))
            response = {"status": "success"}

        elif action == "get_historico_by_processo_id":
            processo_id = request.get("processo_id")
            query = """
                SELECT status_old, status_new, created_at 
                FROM HistoricoMudancaStatus 
                WHERE processo_id = ?
            """
            results = execute_query(query, (processo_id,))
            response = {"historico": results}

        elif action == "get_all_historico_mudanca_status":
            query = """
                SELECT processo_id, status_old, status_new, created_at 
                FROM HistoricoMudancaStatus
            """
            results = execute_query(query)
            response = {"historico": results}

        else:
            response = {"status": "unknown action"}

        client_socket.send(json.dumps(response).encode("utf-8"))
    except Exception as e:
        print(f"Error: {e}")
        client_socket.send(json.dumps({"error": str(e)}).encode("utf-8"))
    finally:
        client_socket.close()
