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

def handle_get_motivo_by_nome(request):
    nome = request.get("nome")
    query = "SELECT nome FROM Motivos WHERE nome = ?"
    results = execute_query(query, (nome,))
    return {"motivo": results[0] if results else None}

def handle_get_motivo_by_id(request):
    id = request.get("id")
    query = "SELECT nome FROM Motivos WHERE motivo_id = ?"
    results = execute_query(query, (id,))
    print(results)
    return {"motivo": results[0] if results else None}

def handle_get_id_motivo_by_nome(request):
    nome = request.get("nome")
    query = "SELECT motivo_id FROM Motivos WHERE nome = ?"
    results = execute_query(query, (nome,))
    return {"id": results[0] if results else None}

def handle_get_all_motivos(request):
    query = "SELECT nome FROM Motivos"
    results = execute_query(query)
    return {"motivos": results}

def handle_add_motivo(request):
    motivo = request.get("motivo")
    query = "INSERT INTO Motivos (nome) VALUES (?)"
    execute_query(query, (motivo["Nome"],))
    return {"status": "success"}

def handle_remove_motivo_by_nome(request):
    nome = request.get("nome")
    query = "DELETE FROM Motivos WHERE nome = ?"
    execute_query(query, (nome,))
    return {"status": "success"}

def handle_update_motivo_by_id(request):
    nome = request.get("nome")
    novo_nome = request.get("novoNome")
    query = "UPDATE Motivos SET nome = ? WHERE nome = ?"
    execute_query(query, (novo_nome or nome, nome))
    return {"status": "success"}

def handle_count_motivos(request):
    query = "SELECT COUNT(*) FROM Motivos"
    results = execute_query(query)
    return {"count": results[0][0]}

def handle_get_reclamado_by_id(request):
    id = request.get("id")
    query = """
        SELECT nome, cpf, cnpj, numero_rua, email, rua, bairro, cidade, uf 
        FROM Reclamados WHERE reclamado_id = ?
    """
    results = execute_query(query, (id,))
    return {"reclamado": results[0] if results else None}

def handle_add_reclamado(request):
    reclamado = request.get("reclamado")
    query = """
        INSERT INTO Reclamados (nome, cpf, cnpj, numero_rua, email, rua, bairro, cidade, uf)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    execute_query(query, (
        reclamado["Nome"], reclamado["Cpf"], reclamado["Cnpj"],
        reclamado["NumeroDaRua"], reclamado["Email"], reclamado["Rua"],
        reclamado["Bairro"], reclamado["Cidade"], reclamado["Estado"]
    ))
    return {"status": "success"}

def handle_update_reclamado_by_id(request):
    id = request.get("id")
    reclamado = request.get("reclamado")
    query = """
        UPDATE Reclamados
        SET nome = ?, cpf = ?, cnpj = ?, numero_rua = ?, email = ?, rua = ?, bairro = ?, cidade = ?, uf = ?
        WHERE reclamado_id = ?
    """
    execute_query(query, (
        reclamado["Nome"], reclamado["Cpf"], reclamado["Cnpj"],
        reclamado["NumeroDaRua"], reclamado["Email"], reclamado["Rua"],
        reclamado["Bairro"], reclamado["Cidade"], reclamado["Estado"], id
    ))
    return {"status": "success"}

def handle_remove_reclamado_by_id(request):
    id = request.get("id")
    query = "DELETE FROM Reclamados WHERE reclamado_id = ?"
    execute_query(query, (id,))
    return {"status": "success"}

def handle_get_all_reclamados(request):
    query = """
        SELECT reclamado_id, nome, cpf, cnpj, numero_rua, email, rua, bairro, cidade, uf 
        FROM Reclamados
    """
    results = execute_query(query)
    return {"reclamados": results}

def handle_count_reclamados(request):
    query = "SELECT COUNT(*) FROM Reclamados"
    results = execute_query(query)
    return {"count": results[0][0]}

def handle_get_reclamante_by_id(request):
    id = request.get("id")
    query = """
        SELECT reclamante_id, nome, rg, cpf FROM Reclamantes WHERE reclamante_id = ?
    """
    results = execute_query(query, (id,))
    print(results)
    return {"reclamante": results[0] if results else None}

def handle_get_reclamante_by_cpf(request):
    cpf = request.get("cpf")
    query = "SELECT reclamante_id, nome, rg, cpf FROM Reclamantes WHERE cpf = ?"
    results = execute_query(query, (cpf,))
    return {"reclamante": results[0] if results else None}

def handle_get_reclamante_by_rg(request):
    rg = request.get("rg")
    query = "SELECT reclamante_id, nome, rg, cpf FROM Reclamantes WHERE rg = ?"
    results = execute_query(query, (rg,))
    return {"reclamante": results[0] if results else None}

def handle_get_all_reclamantes(request):
    query = "SELECT reclamante_id, nome, rg, cpf FROM Reclamantes"
    results = execute_query(query)
    return {"reclamantes": results}

def handle_add_reclamante(request):
    reclamante = request.get("reclamante")
    query = """
        INSERT INTO Reclamantes (nome, rg, cpf)
        VALUES (?, ?, ?)
    """
    execute_query(query, (reclamante["Nome"], reclamante["Rg"], reclamante["Cpf"]))
    return {"status": "success"}

def handle_update_reclamante_by_id(request):
    id = request.get("id")
    reclamante = request.get("reclamante")
    query = """
        UPDATE Reclamantes
        SET nome = ?, rg = ?, cpf = ?
        WHERE reclamante_id = ?
    """
    execute_query(query, (reclamante["Nome"], reclamante["Rg"], reclamante["Cpf"], id))
    return {"status": "success"}

def handle_remove_reclamante_by_id(request):
    id = request.get("id")
    query = "DELETE FROM Reclamantes WHERE reclamante_id = ?"
    execute_query(query, (id,))
    return {"status": "success"}

def handle_count_reclamantes(request):
    query = "SELECT COUNT(*) FROM Reclamantes"
    results = execute_query(query)
    return {"count": results[0][0]}

def handle_get_processo_by_id(request):
    id = request.get("id")
    query = """
        SELECT processo_id, motivo_id, reclamante_id, titulo_processo, status_processo, path_processo, ano, data_audiencia 
        FROM ProcessosAdministrativos WHERE processo_id = ?
    """
    results = execute_query(query, (id,))
    return {"processo": json.dumps(results, default=str) if results else None}

def handle_get_processos_by_status(request):
    status = request.get("status")
    query = "SELECT processo_id, motivo_id, reclamante_id, titulo_processo, status_processo, path_processo, ano, data_audiencia FROM ProcessosAdministrativos WHERE status_processo = ?"
    results = execute_query(query, (status,))
    return {"processos": results}

def handle_get_processos_by_reclamante_id(request):
    reclamante_id = request.get("reclamante_id")
    query = """
        SELECT processo_id, motivo_id, titulo_processo, status_processo, path_processo, ano, data_audiencia 
        FROM ProcessosAdministrativos 
        WHERE reclamante_id = ?
    """
    results = execute_query(query, (reclamante_id,))
    return {"processos": results}

def handle_get_processos_by_motivo_id(request):
    motivo_id = request.get("motivo_id")
    query = """
        SELECT processo_id, motivo_id, titulo_processo, status_processo, path_processo, ano, data_audiencia 
        FROM ProcessosAdministrativos 
        WHERE motivo_id = ?
    """
    results = execute_query(query, (motivo_id,))
    return {"processos": results}

def handle_get_all_processos(request):
    query = """
        SELECT processo_id, motivo_id, reclamante_id, titulo_processo, status_processo, path_processo, ano, data_audiencia 
        FROM ProcessosAdministrativos
    """
    results = execute_query(query)
    return {"processos": json.dumps(results, default=str)}

def handle_new_get_all_processos(request):
    query_processos = """
        SELECT processo_id, motivo_id, reclamante_id, titulo_processo, status_processo, path_processo, ano, data_audiencia 
        FROM ProcessosAdministrativos
    """
    processos = execute_query(query_processos)
    
    query_motivos = "SELECT motivo_id, nome FROM Motivos"
    motivos = execute_query(query_motivos)
    motivos_dict = {m[0]: {"motivo_id": m[0], "nome": m[1]} for m in motivos}
    
    query_reclamantes = "SELECT reclamante_id, nome, rg, cpf FROM Reclamantes"
    reclamantes = execute_query(query_reclamantes)
    reclamantes_dict = {r[0]: {"reclamante_id": r[0], "nome": r[1], "rg": r[2], "cpf": r[3]} for r in reclamantes}
    
    query_relacao = "SELECT processo_id, reclamado_id FROM RelacaoProcessoReclamado"
    relacao = execute_query(query_relacao)
    relacao_dict = {}
    for r in relacao:
        processo_id = r[0]
        reclamado_id = r[1]
        if processo_id not in relacao_dict:
            relacao_dict[processo_id] = []
        relacao_dict[processo_id].append(reclamado_id)
    
    query_reclamados = "SELECT reclamado_id, nome, cpf, cnpj, numero_rua, email, rua, bairro, cidade, uf FROM Reclamados"
    reclamados = execute_query(query_reclamados)
    reclamados_dict = {r[0]: {"reclamado_id": r[0], "nome": r[1], "cpf": r[2], "cnpj": r[3], "numero_rua": r[4], "email": r[5], "rua": r[6], "bairro": r[7], "cidade": r[8], "uf": r[9]} for r in reclamados}
    
    processos_completos = []
    for p in processos:
        processo_id = p[0]
        motivo = motivos_dict.get(p[1], {}) 
        reclamante = reclamantes_dict.get(p[2], {}) 
        reclamados_ids = relacao_dict.get(processo_id, [])
        reclamados = [reclamados_dict.get(rid, {}) for rid in reclamados_ids]
        
        processo_data = {
            "processo_id": processo_id,
            "motivo": motivo,
            "reclamante": reclamante,
            "reclamados": reclamados,
            "titulo_processo": p[3],
            "status_processo": p[4],
            "path_processo": p[5],
            "ano": p[6],
            "data_audiencia": p[7].isoformat() if isinstance(p[7], datetime.datetime) else p[7]
        }
        processos_completos.append(processo_data)
    
    return {"processos": processos_completos}

def handle_add_processo(request):
    import datetime
    processo = request.get("processo")

    nome = processo["Motivo"]["Nome"]
    query = "SELECT motivo_id FROM Motivos WHERE nome = ?"
    results = execute_query(query, (nome,))
    motivo_id = results[0][0]

    reclamante = processo["Reclamante"]
    query = "INSERT INTO Reclamantes (nome, rg, cpf) VALUES (?, ?, ?)"
    execute_query(query, (reclamante["Nome"], reclamante["Rg"], reclamante["Cpf"]))
    query = "SELECT reclamante_id FROM Reclamantes WHERE cpf = ?"
    results = execute_query(query, (reclamante["Cpf"],))
    reclamante_id = results[0][0]

    titulo_processo = processo["Titulo"]
    ano = processo["Ano"]
    status_processo = processo["Status"]
    path_processo = processo["CaminhoDoProcesso"]
    data_audiencia = processo["DataDaAudiencia"]

    query = "INSERT INTO ProcessosAdministrativos (motivo_id, reclamante_id, titulo_processo, status_processo, path_processo, ano, data_audiencia) VALUES (?, ?, ?, ?, ?, ?, ?)"
    execute_query(query, (motivo_id, reclamante_id, titulo_processo, status_processo, path_processo, ano, datetime.datetime.fromisoformat(data_audiencia)))

    reclamado = processo["Reclamado"]
    query = """
        INSERT INTO Reclamados (nome, cpf, cnpj, numero_rua, email, rua, bairro, cidade, uf)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    execute_query(query, (
        reclamado["Nome"], reclamado["Cpf"], reclamado["Cnpj"],
        reclamado["NumeroDaRua"], reclamado["Email"], reclamado["Rua"],
        reclamado["Bairro"], reclamado["Cidade"], reclamado["Estado"]
    ))

    query = "SELECT processo_id FROM ProcessosAdministrativos WHERE titulo_processo = ?"
    results = execute_query(query, (titulo_processo,))
    processo_id = results[0][0]

    query = "SELECT reclamado_id FROM Reclamados WHERE nome = ?"
    results = execute_query(query, (reclamado["Nome"],))
    reclamado_id = results[0][0]

    query = "INSERT INTO RelacaoProcessoReclamado (processo_id, reclamado_id) VALUES (?, ?)"
    execute_query(query, (processo_id, reclamado_id))
    return {"status": "success"}

def handle_update_processo_by_id(request):
    id = request.get("id")
    motivo_id = request.get("motivo_id")
    reclamante_id = request.get("reclamante_id")
    titulo_processo = request.get("titulo_processo")
    ano = request.get("ano")
    status_processo = request.get("status_processo")
    path_processo = request.get("path_processo")
    data_audiencia = request.get("data_audiencia")

    query = "UPDATE ProcessosAdministrativos SET motivo_id = ?, reclamante_id = ?, titulo_processo = ?, status_processo = ?, path_processo = ?, ano = ?, data_audiencia = ? WHERE processo_id = ?"
    execute_query(query, (motivo_id, reclamante_id, titulo_processo, status_processo, path_processo, ano, data_audiencia, id))
    return {"status": "success"}

def handle_remove_processo_by_id(request):
    id = request.get("id")
    query = "DELETE FROM ProcessosAdministrativos WHERE processo_id = ?"
    execute_query(query, (id,))
    return {"status": "success"}

def handle_count_processos(request):
    query = "SELECT COUNT(*) FROM ProcessosAdministrativos"
    results = execute_query(query)
    return {"count": results[0][0]}

def handle_add_relacao_processo_reclamado(request):
    processo_id = request.get("processo_id")
    reclamado_id = request.get("reclamado_id")
    query = "INSERT INTO RelacaoProcessoReclamado (processo_id, reclamado_id) VALUES (?, ?)"
    execute_query(query, (processo_id, reclamado_id))
    return {"status": "success"}

def handle_remove_relacao_processo_reclamado(request):
    processo_id = request.get("processo_id")
    reclamado_id = request.get("reclamado_id")
    query = "DELETE FROM RelacaoProcessoReclamado WHERE processo_id = ? AND reclamado_id = ?"
    execute_query(query, (processo_id, reclamado_id))
    return {"status": "success"}

def handle_get_reclamado_from_relacao_by_processo_id(request):
    processo_id = request.get("processo_id")
    query = "SELECT reclamado_id FROM RelacaoProcessoReclamado WHERE processo_id = ?"
    results = execute_query(query, (processo_id,))
    return {"reclamados": results}

def handle_get_processo_from_relacao_by_reclamado_id(request):
    reclamado_id = request.get("reclamado_id")
    query = "SELECT processo_id FROM RelacaoProcessoReclamado WHERE reclamado_id = ?"
    results = execute_query(query, (reclamado_id,))
    return {"processos": results}

def handle_get_all_relacao_processo_reclamado(request):
    query = "SELECT processo_id, reclamado_id FROM RelacaoProcessoReclamado"
    results = execute_query(query)
    return {"relacao": results}

def handle_add_historico_mudanca_status(request):
    processo_id = request.get("processo_id")
    status_old = request.get("status_old")
    status_new = request.get("status_new")
    query = "INSERT INTO HistoricoMudancaStatus (processo_id, status_old, status_new) VALUES (?, ?, ?)"
    execute_query(query, (processo_id, status_old, status_new))
    return {"status": "success"}

def handle_get_historico_by_processo_id(request):
    processo_id = request.get("processo_id")
    query = "SELECT status_old, status_new, created_at FROM HistoricoMudancaStatus WHERE processo_id = ?"
    results = execute_query(query, (processo_id,))
    return {"historico": results}

def handle_get_all_historico_mudanca_status(request):
    query = "SELECT processo_id, status_old, status_new, created_at FROM HistoricoMudancaStatus"
    results = execute_query(query)
    return {"historico": results}

action_handlers = {
    "get_motivo_by_nome": handle_get_motivo_by_nome,
    "get_motivo_by_id": handle_get_motivo_by_id,
    "get_id_motivo_by_nome": handle_get_id_motivo_by_nome,
    "get_all_motivos": handle_get_all_motivos,
    "add_motivo": handle_add_motivo,
    "remove_motivo_by_nome": handle_remove_motivo_by_nome,
    "update_motivo_by_id": handle_update_motivo_by_id,
    "count_motivos": handle_count_motivos,
    "get_reclamado_by_id": handle_get_reclamado_by_id,
    "add_reclamado": handle_add_reclamado,
    "update_reclamado_by_id": handle_update_reclamado_by_id,
    "remove_reclamado_by_id": handle_remove_reclamado_by_id,
    "get_all_reclamados": handle_get_all_reclamados,
    "count_reclamados": handle_count_reclamados,
    "get_reclamante_by_id": handle_get_reclamante_by_id,
    "get_reclamante_by_cpf": handle_get_reclamante_by_cpf,
    "get_reclamante_by_rg": handle_get_reclamante_by_rg,
    "get_all_reclamantes": handle_get_all_reclamantes,
    "add_reclamante": handle_add_reclamante,
    "update_reclamante_by_id": handle_update_reclamante_by_id,
    "remove_reclamante_by_id": handle_remove_reclamante_by_id,
    "count_reclamantes": handle_count_reclamantes,
    "get_processo_by_id": handle_get_processo_by_id,
    "get_processos_by_status": handle_get_processos_by_status,
    "get_processos_by_reclamante_id": handle_get_processos_by_reclamante_id,
    "get_processos_by_motivo_id": handle_get_processos_by_motivo_id,
    "get_all_processos": handle_get_all_processos,
    "new_get_all_processos": handle_new_get_all_processos,
    "add_processo": handle_add_processo,
    "update_processo_by_id": handle_update_processo_by_id,
    "remove_processo_by_id": handle_remove_processo_by_id,
    "count_processos": handle_count_processos,
    "add_relacao_processo_reclamado": handle_add_relacao_processo_reclamado,
    "remove_relacao_processo_reclamado": handle_remove_relacao_processo_reclamado,
    "get_reclamado_from_relacao_by_processo_id": handle_get_reclamado_from_relacao_by_processo_id,
    "get_processo_from_relacao_by_reclamado_id": handle_get_processo_from_relacao_by_reclamado_id,
    "get_all_relacao_processo_reclamado": handle_get_all_relacao_processo_reclamado,
    "add_historico_mudanca_status": handle_add_historico_mudanca_status,
    "get_historico_by_processo_id": handle_get_historico_by_processo_id,
    "get_all_historico_mudanca_status": handle_get_all_historico_mudanca_status
}

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