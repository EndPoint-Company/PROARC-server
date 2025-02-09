import datetime
import socket
import psycopg2
import json
import global_config
import global_config

# Para saber qual função chamar, veja o dicionário ACTIONS no final do arquivo

def handle_client(client_socket):
    client_socket.settimeout(8)

    try:
        data = client_socket.recv(4096).decode("utf-8").strip()
        request = json.loads(data)
        action = request.get("action")
        
        if action in ACTIONS:
            response = ACTIONS[action](request)
        else:
            response = {"status": "unknown action"}

        client_socket.send(json.dumps(response).encode("utf-8"))
    except Exception as e:
        print(f"Error: {e}")
        client_socket.send(json.dumps({"error": str(e)}).encode("utf-8"))
    finally:
        client_socket.close()


def execute_query(query, params=()):
    conn = psycopg2.connect(**global_config.db_config_pg)
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


def action_insert_reclamacao(request):
    # todo o negocio que ambas tem em comum
    reclamacao = request.get("reclamacao")

    if reclamacao["Motivo"] == None:
        return {"status": "faltando motivo"}  
    if reclamacao["Reclamante"] == None:
        return {"status":"faltando reclamante"} 
    if reclamacao["Reclamados"] == None:
        return {"status":"faltando reclamado"}
    motivo_nome = reclamacao["Motivo"]["Nome"]
    motivo_id = execute_query(QUERIES["get_motivo_id_por_nome"], (motivo_nome,))[0][0]

    reclamante_cpf = reclamacao["Reclamante"]["Cpf"]
    reclamante_id = execute_query(QUERIES["get_reclamante_por_cpf"], (reclamante_cpf,))
    if not bool(reclamante_id):
        execute_query(
            QUERIES["insert_reclamante"],
            (
                reclamacao["Reclamante"]["Nome"],
                reclamacao["Reclamante"]["Rg"],
                reclamacao["Reclamante"]["Cpf"],
                reclamacao["Reclamante"]["Telefone"],
                reclamacao["Reclamante"]["Email"],
            ),
        )
    reclamante_id = execute_query(QUERIES["get_reclamante_por_cpf"], (reclamante_cpf,))[0][0]
     
    procurador_id = None
    if reclamacao["Procurador"] in reclamacao:
        procurador_cpf = reclamacao["Procurador"]["Cpf"]
        procurador_id = execute_query(QUERIES["get_procurador_por_cpf"], (procurador_cpf,))
        if not bool(procurador_id):
            execute_query(QUERIES["insert_procurador"], (reclamacao["Procurador"]["Nome"], reclamacao["Procurador"]["Rg"], reclamacao["Procurador"]["Cpf"], reclamacao["Procurador"]["Telefone"], reclamacao["Procurador"]["Email"]))
        procurador_id = execute_query(QUERIES["get_procurador_por_cpf"], (procurador_cpf,))[0][0]

    reclamados_ids = []
    for i in range(len(reclamacao["Reclamados"])):
        reclamado = reclamacao["Reclamados"][i]
        reclamado_id = execute_query(QUERIES["get_reclamado_id_por_addr"], (reclamado["Numero"], reclamado["Logradouro"], reclamado["Bairro"], reclamado["Cidade"], reclamado["Uf"], reclamado["Cep"]))
        if not bool(reclamado_id):
            execute_query(QUERIES["insert_reclamado"], (reclamado["Nome"], reclamado["Cpf"], reclamado["Cnpj"], reclamado["Numero"], reclamado["Logradouro"], reclamado["Bairro"], reclamado["Cidade"], reclamado["Uf"], reclamado["Telefone"], reclamado["Email"], reclamado["Cep"]))
        reclamado_id = execute_query(QUERIES["get_reclamado_id_por_addr"], (reclamado["Numero"], reclamado["Logradouro"], reclamado["Bairro"], reclamado["Cidade"], reclamado["Uf"], reclamado["Cep"]))[0][0]
        reclamados_ids.append(reclamado_id)

    execute_query(QUERIES["insert_reclamacao"], (motivo_id, reclamante_id, procurador_id, reclamacao["Titulo"], reclamacao["Situacao"], reclamacao["CaminhoDir"], reclamacao["DataAbertura"], reclamacao["Criador"]))
    reclamacao_id = execute_query(QUERIES["get_reclamacao_id_por_titulo"], (reclamacao["Titulo"],))[0][0]

    for i in range(len(reclamados_ids)):
        execute_query(QUERIES["insert_relacao_reclamado_reclamacao"], (reclamacao_id, reclamados_ids[i]))

    if "DataAudiencia" in reclamacao:
        # todo o negocio de reclamacao geral
        execute_query(QUERIES["insert_reclamacao_geral"], (reclamacao_id, reclamacao["DataAudiencia"], reclamacao["Conciliador"]))
    if "Observacao" in reclamacao:
        # todo o negocio de reclamacao enel
        execute_query(QUERIES["insert_reclamacao_enel"], (reclamacao_id, reclamacao["Atendente"], reclamacao["ContatoEnelTelefone"], reclamacao["ContatoEnelEmail"], reclamacao["Observacao"]))

    return {"status": "ok"}


def action_delete_reclamacao_por_titulo(request):
    titulo = request.get("titulo")
    execute_query(QUERIES["delete_reclamacao_por_titulo"], (titulo,))

    return {"status": "ok"}


def action_get_reclamacao_por_titulo(request):
    titulo = request.get("titulo")
    reclamacao = execute_query(QUERIES["get_reclamacao_por_titulo"], (titulo,))

    return {"reclamacao": reclamacao}

def action_get_all_reclamacoes(request):
    query_reclamacoes = """
        SELECT reclamacao_id, motivo_id, reclamante_id, procurador_id, titulo, situacao, caminho_dir, data_abertura, ultima_mudanca, criador, created_at
        FROM Reclamacoes
    """
    reclamacoes = execute_query(query_reclamacoes)
    
    query_motivos = "SELECT motivo_id, nome FROM Motivos"
    motivos = execute_query(query_motivos)
    motivos_dict = {m[0]: {"motivo_id": m[0], "nome": m[1]} for m in motivos}
    
    query_reclamantes = "SELECT reclamante_id, nome, rg, cpf FROM Reclamantes"
    reclamantes = execute_query(query_reclamantes)
    reclamantes_dict = {
        r[0]: {"reclamante_id": r[0], "nome": r[1], "rg": r[2], "cpf": r[3]}
        for r in reclamantes
    }
    
    query_procuradores = "SELECT procurador_id, nome, rg, cpf, telefone, email, created_at FROM Procuradores"
    procuradores = execute_query(query_procuradores)
    procuradores_dict = {
        p[0]: {
            "procurador_id": p[0],
            "nome": p[1],
            "rg": p[2],
            "cpf": p[3],
            "telefone": p[4],
            "email": p[5],
            "created_at": p[6].isoformat() if hasattr(p[6], "isoformat") else p[6]
        }
        for p in procuradores
    }
    
    query_relacao = "SELECT reclamacao_id, reclamado_id FROM RelacaoProcessoReclamado"
    relacao = execute_query(query_relacao)
    relacao_dict = {}
    for r in relacao:
        reclamacao_id = r[0]
        reclamado_id = r[1]
        if reclamacao_id not in relacao_dict:
            relacao_dict[reclamacao_id] = []
        relacao_dict[reclamacao_id].append(reclamado_id)
    
    query_reclamados = """
        SELECT reclamado_id, nome, cpf, cnpj, numero_addr, logradouro_addr, bairro_addr, cidade_addr, uf_addr, telefone, email, cep, created_at
        FROM Reclamados
    """
    reclamados = execute_query(query_reclamados)
    reclamados_dict = {}
    for r in reclamados:
        reclamados_dict[r[0]] = {
            "reclamado_id": r[0],
            "nome": r[1],
            "cpf": r[2],
            "cnpj": r[3],
            "numero_addr": r[4],
            "logradouro_addr": r[5],
            "bairro_addr": r[6],
            "cidade_addr": r[7],
            "uf_addr": r[8],
            "telefone": r[9],
            "email": r[10],
            "cep": r[11],
            "created_at": r[12].isoformat() if hasattr(r[12], "isoformat") else r[12]
        }
    
    reclamacoes_completas = []
    for rec in reclamacoes:
        reclamacao_id = rec[0]
        motivo = motivos_dict.get(rec[1], {})
        reclamante = reclamantes_dict.get(rec[2], {})
        procurador = procuradores_dict.get(rec[3], {}) if rec[3] is not None else {}
        reclamados_ids = relacao_dict.get(reclamacao_id, [])
        reclamados_list = [reclamados_dict.get(rid, {}) for rid in reclamados_ids]
        
        reclamacao_data = {
            "reclamacao_id": reclamacao_id,
            "motivo": motivo,
            "reclamante": reclamante,
            "procurador": procurador,
            "titulo": rec[4],
            "situacao": rec[5],
            "caminho_dir": rec[6],
            "data_abertura": rec[7].isoformat() if hasattr(rec[7], "isoformat") else rec[7],
            "ultima_mudanca": rec[8].isoformat() if hasattr(rec[8], "isoformat") else rec[8],
            "criador": rec[9],
            "created_at": rec[10].isoformat() if hasattr(rec[10], "isoformat") else rec[10],
            "reclamados": reclamados_list
        }
        reclamacoes_completas.append(reclamacao_data)
    
    return {"reclamacoes": reclamacoes_completas}


def action_get_all_reclamacoes_completo(request):
    import datetime

    query_reclamacoes = """
        SELECT reclamacao_id, motivo_id, reclamante_id, procurador_id, titulo, situacao, caminho_dir, 
               data_abertura, ultima_mudanca, criador, created_at
        FROM Reclamacoes
    """
    reclamacoes = execute_query(query_reclamacoes)
    
    query_motivos = "SELECT motivo_id, nome FROM Motivos"
    motivos = execute_query(query_motivos)
    motivos_dict = { m[0]: {"motivo_id": m[0], "nome": m[1]} for m in motivos }
    
    query_reclamantes = "SELECT reclamante_id, nome, rg, cpf FROM Reclamantes"
    reclamantes = execute_query(query_reclamantes)
    reclamantes_dict = {
        r[0]: {"reclamante_id": r[0], "nome": r[1], "rg": r[2], "cpf": r[3]}
        for r in reclamantes
    }
    
    query_procuradores = "SELECT procurador_id, nome, rg, cpf, telefone, email, created_at FROM Procuradores"
    procuradores = execute_query(query_procuradores)
    procuradores_dict = {
        p[0]: {
            "procurador_id": p[0],
            "nome": p[1],
            "rg": p[2],
            "cpf": p[3],
            "telefone": p[4],
            "email": p[5],
            "created_at": p[6].isoformat() if hasattr(p[6], "isoformat") else p[6]
        }
        for p in procuradores
    }
    
    query_relacao = "SELECT reclamacao_id, reclamado_id FROM RelacaoProcessoReclamado"
    relacoes = execute_query(query_relacao)
    relacao_dict = {}
    for r in relacoes:
        rec_id = r[0]
        reclamado_id = r[1]
        if rec_id not in relacao_dict:
            relacao_dict[rec_id] = []
        relacao_dict[rec_id].append(reclamado_id)
    
    query_reclamados = """
        SELECT reclamado_id, nome, cpf, cnpj, numero_addr, logradouro_addr, bairro_addr, cidade_addr, uf_addr, telefone, email, cep, created_at
        FROM Reclamados
    """
    reclamados = execute_query(query_reclamados)
    reclamados_dict = {}
    for r in reclamados:
        reclamados_dict[r[0]] = {
            "reclamado_id": r[0],
            "nome": r[1],
            "cpf": r[2],
            "cnpj": r[3],
            "numero_addr": r[4],
            "logradouro_addr": r[5],
            "bairro_addr": r[6],
            "cidade_addr": r[7],
            "uf_addr": r[8],
            "telefone": r[9],
            "email": r[10],
            "cep": r[11],
            "created_at": r[12].isoformat() if hasattr(r[12], "isoformat") else r[12]
        }
    
    query_reclamacoes_geral = "SELECT reclamacao_id, data_audiencia, conciliador FROM ReclamacoesGeral"
    geral = execute_query(query_reclamacoes_geral)
    geral_dict = {}
    for g in geral:
        geral_dict[g[0]] = {
            "data_audiencia": g[1].isoformat() if hasattr(g[1], "isoformat") else g[1],
            "conciliador": g[2]
        }
    
    query_reclamacoes_enel = """
        SELECT reclamacao_id, atendente, contato_enel_telefone, contato_enel_email, observacao
        FROM ReclamacoesEnel
    """
    enel = execute_query(query_reclamacoes_enel)
    enel_dict = {}
    for e in enel:
        enel_dict[e[0]] = {
            "atendente": e[1],
            "contato_enel_telefone": e[2],
            "contato_enel_email": e[3],
            "observacao": e[4]
        }
    
    reclamacoes_completas = []
    for rec in reclamacoes:
        rec_id = rec[0]
        motivo = motivos_dict.get(rec[1], {})
        reclamante = reclamantes_dict.get(rec[2], {})
        procurador = procuradores_dict.get(rec[3], {}) if rec[3] is not None else {}
        titulo = rec[4]
        situacao = rec[5]
        caminho_dir = rec[6]
        data_abertura = rec[7].isoformat() if hasattr(rec[7], "isoformat") else rec[7]
        ultima_mudanca = rec[8].isoformat() if hasattr(rec[8], "isoformat") else rec[8]
        criador = rec[9]
        created_at = rec[10].isoformat() if hasattr(rec[10], "isoformat") else rec[10]
        
        reclamados_ids = relacao_dict.get(rec_id, [])
        reclamados_list = [reclamados_dict.get(rid, {}) for rid in reclamados_ids]
        
        reclamacoes_geral = geral_dict.get(rec_id, {})    
        reclamacoes_enel = enel_dict.get(rec_id, {})      
        
        reclamacao_completa = {
            "reclamacao_id": rec_id,
            "motivo": motivo,
            "reclamante": reclamante,
            "procurador": procurador,
            "titulo": titulo,
            "situacao": situacao,
            "caminho_dir": caminho_dir,
            "data_abertura": data_abertura,
            "ultima_mudanca": ultima_mudanca,
            "criador": criador,
            "created_at": created_at,
            "reclamados": reclamados_list,
            "reclamacoes_geral": reclamacoes_geral,
            "reclamacoes_enel": reclamacoes_enel
        }
        reclamacoes_completas.append(reclamacao_completa)
    
    return {"reclamacoes": reclamacoes_completas}



def action_update_situacao_reclamacao_por_titulo(request):
    titulo = request.get("titulo")
    situacao_new = request.get("situacao")

    reclamacao_id = execute_query(QUERIES["get_reclamacao_id_por_titulo"], (titulo,))[0][0]
    situacao_old = execute_query(QUERIES["get_reclamacao_situacao_por_titulo"], (titulo,))[0][0]

    execute_query(QUERIES["update_situacao_reclamacao_por_titulo"], (situacao_new, titulo))
    execute_query(QUERIES["insert_situacao_mudanca_historico"], (reclamacao_id, situacao_old, situacao_new))

    return {"status": "ok"}


def action_count_reclamacoes(request):
    quantidade = execute_query(QUERIES["count_reclamacoes"])

    return {"count": quantidade[0][0]}


def action_count_reclamacoes_enel(request):
    quantidade = execute_query(QUERIES["count_reclamacoes_enel"])

    return {"count": quantidade[0][0]}


def action_count_reclamacoes_geral(request):
    quantidade = execute_query(QUERIES["count_reclamacoes_geral"])

    return {"count": quantidade[0][0]}


def action_get_reclamante_por_id(request):
    id = request.get("id")
    query = """
        SELECT reclamante_id, nome, rg, cpf, telefone, email FROM Reclamantes WHERE reclamante_id = (%s)
    """
    results = execute_query(query, (id,))

    return {"reclamante": results[0] if results else None}


def action_get_reclamante_por_cpf(request):
    cpf = request.get("cpf")
    query = "SELECT reclamante_id, nome, rg, cpf, telefone, email FROM Reclamantes WHERE cpf = (%s)"
    results = execute_query(query, (cpf,))
    return {"reclamante": results[0] if results else None}


def action_get_reclamante_por_rg(request):
    rg = request.get("rg")
    query = "SELECT reclamante_id, nome, rg, cpf, telefone, email FROM Reclamantes WHERE rg = (%s)"
    results = execute_query(query, (rg,))
    return {"reclamante": results[0] if results else None}


def action_get_all_reclamantes(request):
    query = "SELECT reclamante_id, nome, rg, cpf, telefone, email FROM Reclamantes"
    results = execute_query(query)
    return {"reclamantes": results}


def action_insert_reclamante(request):
    reclamante = request.get("reclamante")
    query = """
        INSERT INTO Reclamantes (nome, rg, cpf, telefone, email)
        VALUES ((%s), (%s), (%s), (%s), (%s))
    """
    execute_query(query, (reclamante["Nome"], reclamante["Rg"], reclamante["Cpf"], reclamante["Telefone"], reclamante["Email"]))
    return {"status": "success"}


def action_update_reclamante_by_id(request):
    id = request.get("id")
    reclamante = request.get("reclamante")
    query = """
        UPDATE Reclamantes
        SET nome = (%s), rg = (%s), cpf = (%s), telefone = (%s), email = (%s)
        WHERE reclamante_id = (%s)
    """
    execute_query(query, (reclamante["Nome"], reclamante["Rg"], reclamante["Cpf"], reclamante["Telefone"], reclamante["Email"], id))
    return {"status": "success"}


def action_delete_reclamante_by_id(request):
    id = request.get("id")
    query = "DELETE FROM Reclamantes WHERE reclamante_id = (%s)"
    execute_query(query, (id,))
    return {"status": "success"}


def action_count_reclamantes(request):
    query = "SELECT COUNT(*) FROM Reclamantes"
    results = execute_query(query)
    return {"count": results[0][0]}


def action_get_reclamado_por_id(request):
    id = request.get("id")
    query = """
        SELECT nome, cpf, cnpj, numero_addr, logradouro_addr, bairro_addr, cidade_addr, uf_addr, cep, telefone, email
        FROM Reclamados WHERE reclamado_id = (%s)
    """
    results = execute_query(query, (id,))
    return {"reclamado": results[0] if results else None}

def action_insert_reclamado(request):
    reclamado = request.get("reclamado")
    query = """
        INSERT INTO Reclamados (nome, cpf, cnpj, numero_addr, logradouro_addr, bairro_addr, cidade_addr, uf_addr, cep, telefone, email)
        VALUES ((%s), (%s), (%s), (%s), (%s), (%s), (%s), (%s), (%s), (%s), (%s))
    """
    execute_query(query, (
        reclamado["Nome"], reclamado["Cpf"], reclamado["Cnpj"],
        reclamado["Numero"], reclamado["Logradouro"], reclamado["Bairro"],
        reclamado["Cidade"], reclamado["Uf"], reclamado["Cep"], reclamado["Telefone"], reclamado["Email"]
    ))
    return {"status": "success"}

def action_update_reclamado_por_id(request):
    id = request.get("id")
    reclamado = request.get("reclamado")
    query = """
        UPDATE Reclamados
        SET nome = (%s), cpf = (%s), cnpj = (%s), numero_addr = (%s), logradouro_addr = (%s), bairro_addr = (%s), cidade_addr = (%s), uf_addr = (%s), cep = (%s), telefone = (%s), email = (%s)
        WHERE reclamado_id = (%s)
    """
    execute_query(query, (
        reclamado["Nome"], reclamado["Cpf"], reclamado["Cnpj"],
        reclamado["Numero"], reclamado["Logradouro"], reclamado["Bairro"],
        reclamado["Cidade"], reclamado["Uf"], reclamado["Cep"], reclamado["Telefone"], reclamado["Email"], id
    ))
    return {"status": "success"}

def action_delete_reclamado_por_id(request):
    id = request.get("id")
    query = "DELETE FROM Reclamados WHERE reclamado_id = (%s)"
    execute_query(query, (id,))
    return {"status": "success"}


def action_get_all_reclamados(request):
    query = """
        SELECT reclamado_id, nome, cpf, cnpj, numero_addr, logradouro_addr, bairro_addr, cidade_addr, uf_addr, cep, telefone, email 
        FROM Reclamados
    """
    results = execute_query(query)
    return {"reclamados": results}


def action_count_reclamados(request):
    query = "SELECT COUNT(*) FROM Reclamados"
    results = execute_query(query)
    return {"count": results[0][0]}


def action_get_motivo_por_nome(request):
    nome = request.get("nome")
    query = "SELECT nome FROM Motivos WHERE nome = (%s)"
    results = execute_query(query, (nome,))
    return {"motivo": results[0] if results else None}


def action_get_motivo_por_id(request):
    id = request.get("id")
    query = "SELECT nome FROM Motivos WHERE motivo_id = (%s)"
    results = execute_query(query, (id,))

    return {"motivo": results[0] if results else None}


def action_get_id_motivo_por_nome(request):
    nome = request.get("nome")
    query = "SELECT motivo_id FROM Motivos WHERE nome = (%s)"
    results = execute_query(query, (nome,))
    return {"id": results[0] if results else None}


def action_get_all_motivos(request):
    query = "SELECT nome FROM Motivos"
    results = execute_query(query)
    return {"motivos": results}


def action_insert_motivo(request):
    motivo = request.get("motivo")
    query = "INSERT INTO Motivos (nome) VALUES ((%s))"
    execute_query(query, (motivo["Nome"],))
    return {"status": "success"}


def action_delete_motivo_por_nome(request):
    nome = request.get("nome")
    query = "DELETE FROM Motivos WHERE nome = (%s)"
    execute_query(query, (nome,))
    return {"status": "success"}


def action_update_motivo_por_id(request):
    nome = request.get("nome")
    novo_nome = request.get("novoNome")
    query = "UPDATE Motivos SET nome = (%s) WHERE nome = (%s)"
    execute_query(query, (novo_nome or nome, nome))
    return {"status": "success"}


def action_count_motivos(request):
    query = "SELECT COUNT(*) FROM Motivos"
    results = execute_query(query)
    return {"count": results[0][0]}





QUERIES = {
    "get_reclamacao_id_por_titulo": "SELECT reclamacao_id FROM Reclamacoes WHERE titulo = (%s)",
    "get_reclamado_id_por_addr": "SELECT reclamado_id FROM Reclamados WHERE numero_addr = (%s) AND logradouro_addr = (%s) AND bairro_addr = (%s) AND cidade_addr = (%s) AND uf_addr = (%s) AND cep = (%s)",
    "get_reclamado_id_por_cnpj": "SELECT reclamado_id FROM Reclamados WHERE cnpj = (%s)",
    "get_reclamante_por_cpf": "SELECT reclamante_id FROM Reclamantes WHERE cpf = (%s)",
    "get_procurador_por_cpf": "SELECT procurador_id FROM Procuradores WHERE cpf = (%s)",
    "get_reclamacao_situacao_por_titulo": "SELECT situacao FROM Reclamacoes WHERE titulo = (%s)",
    "get_motivo_id_por_nome": "SELECT motivo_id FROM Motivos WHERE nome = (%s)",
    "get_reclamante_id_por_cpf": "SELECT reclamante_id FROM Reclamantes WHERE cpf = (%s)",
    "get_all_reclamacoes": "SELECT * FROM Reclamacoes",
    "insert_reclamante": "INSERT INTO Reclamantes (nome, rg, cpf, telefone, email) VALUES (%s, %s, %s, %s, %s)",
    "insert_relacao_reclamado_reclamacao": "INSERT INTO RelacaoProcessoReclamado (reclamacao_id, reclamado_id) VALUES (%s, %s)",
    "insert_reclamado": "INSERT INTO Reclamados (nome, cpf, cnpj, numero_addr, logradouro_addr, bairro_addr, cidade_addr, uf_addr, telefone, email, cep) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
    "insert_reclamacao": "INSERT INTO Reclamacoes (motivo_id, reclamante_id, procurador_id, titulo, situacao, caminho_dir, data_abertura, criador) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
    "insert_reclamacao_geral": "INSERT INTO ReclamacoesGeral (reclamacao_id, data_audiencia, conciliador) VALUES (%s, %s, %s)",
    "insert_reclamacao_enel": "INSERT INTO ReclamacoesEnel (reclamacao_id, atendente, contato_enel_telefone, contato_enel_email, observacao) VALUES (%s, %s, %s, %s, %s)",
    "insert_situacao_mudanca_historico": "INSERT INTO HistoricoMudancaSituacao (reclamacao_id, situacao_old, situacao_new) VALUES (%s, %s, %s)",
    "update_situacao_reclamacao_por_titulo": "UPDATE Reclamacoes SET situacao = (%s) WHERE titulo = (%s)",
    "delete_reclamacao_por_titulo": "DELETE FROM Reclamacoes WHERE titulo = (%s)",
    "count_reclamacoes": "SELECT COUNT(*) FROM Reclamacoes",
    "count_reclamacoes_enel": "SELECT COUNT(*) FROM ReclamacoesEnel",
    "count_reclamacoes_geral": "SELECT COUNT(*) FROM ReclamacoesGeral",
}

ACTIONS = {
    "insert_reclamacao": action_insert_reclamacao,
    "delete_reclamacao_por_titulo": action_delete_reclamacao_por_titulo,
    "get_all_reclamacoes": action_get_all_reclamacoes,
    "get_all_reclamacoes_completo": action_get_all_reclamacoes_completo,
    "update_situacao_reclamacao_por_titulo": action_update_situacao_reclamacao_por_titulo,
    "count_reclamacoes": action_count_reclamacoes,
    "count_reclamacoes_enel": action_count_reclamacoes_enel,
    "count_reclamacoes_geral": action_count_reclamacoes_geral,
    "get_reclamante_por_id": action_get_reclamante_por_id,
    "get_reclamante_por_cpf": action_get_reclamante_por_cpf,
    "get_reclamante_por_rg": action_get_reclamante_por_rg,
    "get_all_reclamantes": action_get_all_reclamantes,
    "insert_reclamante": action_insert_reclamante,
    "update_reclamante_por_id": action_update_reclamante_by_id,
    "delete_reclamante_por_id": action_delete_reclamante_by_id,
    "count_reclamantes": action_count_reclamantes,
    "get_reclamado_por_id": action_get_reclamado_por_id,
    "insert_reclamado": action_insert_reclamado,
    "update_reclamado_por_id": action_update_reclamado_por_id,
    "delete_reclamado_por_id": action_delete_reclamado_por_id,
    "get_all_reclamados": action_get_all_reclamados,
    "count_reclamados": action_count_reclamados,
    "get_motivo_por_nome": action_get_motivo_por_nome,
    "get_motivo_por_id": action_get_motivo_por_id,
    "get_id_motivo_por_nome": action_get_id_motivo_por_nome,
    "get_all_motivos": action_get_all_motivos,
    "insert_motivo": action_insert_motivo,
    "delete_motivo_por_nome": action_delete_motivo_por_nome,
    "update_motivo_por_id": action_update_motivo_por_id,
    "count_motivos": action_count_motivos,
}
