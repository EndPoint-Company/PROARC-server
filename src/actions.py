import datetime
import psycopg2
import json
import config.database as database
import config.database as database
from src.utils.colors import Colors as colors

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
        print(f"{colors.LIGHT_RED}Error: {e}{colors.END}")
        client_socket.send(json.dumps({"error": str(e)}).encode("utf-8"))
    finally:
        client_socket.close()


def execute_query(query, params=()):
    conn = psycopg2.connect(**database.credentials)
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
    reclamacao = request.get("reclamacao")
   # print(f"[DB] Reclamação: {json.dumps(json.loads(reclamacao), indent=4)}")

    if reclamacao["Motivo"] == None:
        return {"status": "faltando motivo"}  
    if reclamacao["Reclamante"] == None:
        return {"status":"faltando reclamante"} 
    if reclamacao["Reclamados"] == None:
        return {"status":"faltando reclamado"}
    
    motivo_nome = reclamacao["Motivo"]["Nome"]
    print(motivo_nome)
    motivo_id = execute_query(QUERIES["get_motivo_id_por_nome"], (motivo_nome,))[0][0]
    print(motivo_id)

    reclamante_cpf = reclamacao["Reclamante"]["Cpf"]
    print(reclamante_cpf)
    reclamante_id = execute_query(QUERIES["get_reclamante_por_cpf"], (reclamante_cpf,))
    print (reclamante_id)

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
    print(reclamante_id)
     
    procurador_id = None
    if reclamacao.get("Procurador"):  # Verifica se "Procurador" existe e não é None
        procurador_cpf = reclamacao["Procurador"].get("Cpf")
    
        if procurador_cpf:  # Verifica se o CPF do procurador não é None
            procurador_id_result = execute_query(QUERIES["get_procurador_por_cpf"], (procurador_cpf,))
        
            if not procurador_id_result:  # Se não encontrou, insere o procurador
                execute_query(QUERIES["insert_procurador"], (
                    reclamacao["Procurador"]["Nome"], 
                    reclamacao["Procurador"]["Rg"], 
                    procurador_cpf, 
                    reclamacao["Procurador"]["Telefone"], 
                    reclamacao["Procurador"]["Email"]
                ))
                procurador_id_result = execute_query(QUERIES["get_procurador_por_cpf"], (procurador_cpf,))
            procurador_id = procurador_id_result[0][0]
    print(procurador_id)

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

    print("[DB] Reclamação inserida com sucesso")
    return {"status": "ok"}


def action_delete_reclamacao_por_titulo(request):
    titulo = request.get("titulo")
    execute_query(QUERIES["delete_reclamacao_por_titulo"], (titulo,))

    print("[DB] Reclamação deletada com sucesso")
    return {"status": "ok"}


def action_update_reclamacao(request):
    titulo = request.get("titulo")
    reclamacao = request.get("NovaReclamacao")

    if reclamacao["Motivo"] is None:
        return {"status": "faltando motivo"}  
    if reclamacao["Reclamante"] is None:
        return {"status":"faltando reclamante"} 
    if reclamacao["Reclamados"] is None:
        return {"status":"faltando reclamado"}
    
    situacao_old_result = execute_query(QUERIES["get_reclamacao_situacao_por_titulo"], (titulo,))[0][0]

    # Obter o ID da reclamação
    reclamacao_id_result = execute_query(QUERIES["get_reclamacao_id_por_titulo"], (titulo,))
    if not reclamacao_id_result:
        return {"status": "reclamacao_nao_encontrada"}
    reclamacao_id = reclamacao_id_result[0][0]

    # Atualizar o motivo
    motivo_nome = reclamacao["Motivo"]["Nome"] 
    motivo_id_result = execute_query(QUERIES["get_motivo_id_por_nome"], (motivo_nome,))
    if not motivo_id_result:
        execute_query(QUERIES["insert_motivo"], (motivo_nome,))
        motivo_id_result = execute_query(QUERIES["get_motivo_id_por_nome"], (motivo_nome,))
    motivo_id = motivo_id_result[0][0]

    # Atualizar o reclamante
    reclamante_cpf = reclamacao["Reclamante"]["Cpf"]
    reclamante_id_result = execute_query(QUERIES["get_reclamante_por_cpf"], (reclamante_cpf,))
    if not reclamante_id_result:
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
        reclamante_id_result = execute_query(QUERIES["get_reclamante_por_cpf"], (reclamante_cpf,))
    reclamante_id = reclamante_id_result[0][0]

    # Atualizar o procurador (se existir)
    procurador_id = None
    if reclamacao.get("Procurador"):  # Verifica se "Procurador" existe e não é None
        procurador_cpf = reclamacao["Procurador"].get("Cpf")
    
        if procurador_cpf:  # Verifica se o CPF do procurador não é None
            procurador_id_result = execute_query(QUERIES["get_procurador_por_cpf"], (procurador_cpf,))
        
            if not procurador_id_result:  # Se não encontrou, insere o procurador
                execute_query(QUERIES["insert_procurador"], (
                    reclamacao["Procurador"]["Nome"], 
                    reclamacao["Procurador"]["Rg"], 
                    procurador_cpf, 
                    reclamacao["Procurador"]["Telefone"], 
                    reclamacao["Procurador"]["Email"]
                ))
                procurador_id_result = execute_query(QUERIES["get_procurador_por_cpf"], (procurador_cpf,))
            procurador_id = procurador_id_result[0][0]
    print(procurador_id)

    # Atualizar a reclamação
    execute_query(QUERIES["update_reclamacao"], (
        motivo_id,
        reclamante_id,
        procurador_id,
        reclamacao["Titulo"],
        reclamacao["Situacao"],
        reclamacao["CaminhoDir"],
        reclamacao["DataAbertura"],
        reclamacao["Criador"],
        reclamacao_id
    ))
    
    # Atualizar a relação com os reclamados
    execute_query("DELETE FROM RelacaoProcessoReclamado WHERE reclamacao_id = (%s)", (reclamacao_id,))
    for reclamado in reclamacao["Reclamados"]:
        reclamado_id_result = execute_query(QUERIES["get_reclamado_id_por_addr"], (
            reclamado["Numero"], reclamado["Logradouro"], reclamado["Bairro"], reclamado["Cidade"], reclamado["Uf"], reclamado["Cep"]
        ))
        if not reclamado_id_result:  # Se não encontrou o reclamado
            execute_query(QUERIES["insert_reclamado"], (
                reclamado["Nome"], reclamado["Cpf"], reclamado["Cnpj"], reclamado["Numero"], reclamado["Logradouro"], reclamado["Bairro"], reclamado["Cidade"], reclamado["Uf"], reclamado["Telefone"], reclamado["Email"], reclamado["Cep"]
            ))
            reclamado_id_result = execute_query(QUERIES["get_reclamado_id_por_addr"], (
                reclamado["Numero"], reclamado["Logradouro"], reclamado["Bairro"], reclamado["Cidade"], reclamado["Uf"], reclamado["Cep"]
            ))
        
        reclamado_id = reclamado_id_result[0][0]
        print(reclamado_id)
        execute_query(QUERIES["insert_relacao_reclamado_reclamacao"], (reclamacao_id, reclamado_id))

    # Registrar mudança de situação, se houver
    
    if situacao_old_result:
        print("situacao antiga - " + situacao_old_result)
        print("situacao atual - " + reclamacao["Situacao"])
        if situacao_old_result != reclamacao["Situacao"]:
            execute_query(QUERIES["insert_situacao_mudanca_historico"], (reclamacao_id, situacao_old_result, reclamacao["Situacao"]))
    
    # Atualizar informações específicas de ReclamacoesGeral e ReclamacoesEnel, se necessário
    if "DataAudiencia" in reclamacao:
        execute_query(QUERIES["update_reclamacao_geral"], (
            reclamacao["DataAudiencia"], 
            reclamacao["Conciliador"],
            reclamacao_id
        ))

    if "Observacao" in reclamacao:
        execute_query(QUERIES["update_reclamacao_enel"], (
            reclamacao["Atendente"], 
            reclamacao["ContatoEnelTelefone"], 
            reclamacao["ContatoEnelEmail"], 
            reclamacao["Observacao"],
            reclamacao_id
        ))

    print("[DB] Reclamação atualizada com sucesso")
    return {"status": "ok"}


def action_get_reclamacao_por_titulo(request):
    import orjson
    titulo = request.get("titulo")    
    reclamacao = execute_query(QUERIES["get_reclamacao_por_titulo"], (titulo,))
    
    motivoId = reclamacao[0][1]
    motivos = {"nome motivo": {"nome": m[0]} for m in execute_query("SELECT nome FROM Motivos WHERE motivo_id = (%s)", (motivoId,))}

    reclamanteId = reclamacao[0][2]
    reclamantes = {"reclamantes": {"nome": r[0], "rg": r[1], "cpf": r[2], "telefone": r[3], "email": r[4]} for r in execute_query("SELECT nome, rg, cpf, telefone, email FROM Reclamantes WHERE reclamante_id = (%s)", (reclamanteId,))}

    procuradorId = reclamacao[0][3]
    procuradores = {str(p[0]): {
        "nome": p[1], "rg": p[2], "cpf": p[3], "telefone": p[4],
        "email": p[5], "created_at": serialize_datetime(p[6])
    } for p in execute_query("SELECT * FROM Procuradores WHERE procurador_id = (%s)",(procuradorId,))}

    # Criar relação entre reclamações e reclamados
    relacaoId = reclamacao[0][0]
    reclamadosIds = execute_query("SELECT reclamado_id from relacaoprocessoreclamado where reclamacao_id = (%s)",(relacaoId,))

    reclamado_ids = [r[0] for r in reclamadosIds]
    
    # Criar dicionário de reclamados apenas se houver IDs para buscar
    reclamados = {}
    if reclamado_ids:
        placeholders = ', '.join(['%s'] * len(reclamado_ids))  # Criar os placeholders (%s, %s, %s, ...)
        query = f"SELECT reclamado_id, nome, cpf, cnpj, numero_addr, logradouro_addr, bairro_addr, cidade_addr, uf_addr, telefone, email, cep, created_at FROM Reclamados WHERE reclamado_id IN ({placeholders})"
        reclamados = {r[0]: {
            "nome": r[1], "cpf": r[2], "cnpj": r[3], "numero_addr": r[4],
            "logradouro_addr": r[5], "bairro_addr": r[6], "cidade_addr": r[7],
            "uf_addr": r[8], "telefone": r[9], "email": r[10], "cep": r[11],
            "created_at": serialize_datetime(r[12])
        } for r in execute_query(query, tuple(reclamado_ids))}

    geral_dict = {
        g[0]: {"data_audiencia": serialize_datetime(g[1]), "conciliador": g[2]}
        for g in execute_query("SELECT reclamacao_id, data_audiencia, conciliador FROM ReclamacoesGeral")
    }

    # Criar dicionário de reclamações Enel
    enel_dict = {
        e[0]: {"atendente": e[1], "contato_enel_telefone": e[2], "contato_enel_email": e[3], "observacao": e[4]}
        for e in execute_query("SELECT reclamacao_id, atendente, contato_enel_telefone, contato_enel_email, observacao FROM ReclamacoesEnel")
    }

    # Criar lista final de reclamações sem referências circulares
    reclamacoes_completas = []
    for rec in reclamacao:
        rec_id = rec[0]

        reclamacao_completa = {
            "motivo": motivos,  
            "reclamante": reclamantes,  
            "procurador": procuradores,  
            "titulo": rec[4],
            "situacao": rec[5],
            "caminho_dir": rec[6],
            "data_abertura": serialize_datetime(rec[7]),
            "ultima_mudanca": serialize_datetime(rec[8]),
            "criador": rec[9],
            "created_at": serialize_datetime(rec[10]),
            "reclamados": [dict(reclamados.get(rid, {})) for rid in reclamado_ids],
            "reclamacoes_geral": dict(geral_dict.get(rec_id, {})),
            "reclamacoes_enel": dict(enel_dict.get(rec_id, {}))
        }
        reclamacoes_completas.append(reclamacao_completa)     

    # Serializar JSON sem erro de referência circular
    return_json = orjson.dumps({"reclamacoes": reclamacoes_completas}, default=serialize_datetime).decode()

    print(f"[DB] {return_json}")

    return return_json


def serialize_datetime(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    return obj


def aux_all_recl(request, reclamacoes):
    import orjson

    motivos = {m[0]: {"nome": m[1]} for m in execute_query(QUERIES["get_all_motivos"])}

    reclamantes = {r[0]: {"nome": r[1], "rg": r[2], "cpf": r[3], "telefone": r[4], "email": r[5]} for r in execute_query(QUERIES["get_all_reclamantes"])}

    procuradores = {p[0]: {
        "nome": p[1], "rg": p[2], "cpf": p[3], "telefone": p[4],
        "email": p[5], "created_at": serialize_datetime(p[6])
    } for p in execute_query(QUERIES["get_all_procuradores"])}

    # Criar relação entre reclamações e reclamados
    relacoes = execute_query("SELECT reclamacao_id, reclamado_id FROM RelacaoProcessoReclamado")
    relacao_dict = {}
    for rec_id, reclamado_id in relacoes:
        relacao_dict.setdefault(rec_id, []).append(reclamado_id)

    # Criar dicionário de reclamados
    reclamados = {
        r[0]: {
            "nome": r[1], "cpf": r[2], "cnpj": r[3], "numero_addr": r[4],
            "logradouro_addr": r[5], "bairro_addr": r[6], "cidade_addr": r[7],
            "uf_addr": r[8], "telefone": r[9], "email": r[10], "cep": r[11],
            "created_at": serialize_datetime(r[12])
        } for r in execute_query(QUERIES["get_all_reclamados"])
    }

    # Criar dicionário de informações gerais das reclamações
    geral_dict = {
        g[0]: {"data_audiencia": serialize_datetime(g[1]), "conciliador": g[2]}
        for g in execute_query("SELECT reclamacao_id, data_audiencia, conciliador FROM ReclamacoesGeral")
    }

    # Criar dicionário de reclamações Enel
    enel_dict = {
        e[0]: {"atendente": e[1], "contato_enel_telefone": e[2], "contato_enel_email": e[3], "observacao": e[4]}
        for e in execute_query("SELECT reclamacao_id, atendente, contato_enel_telefone, contato_enel_email, observacao FROM ReclamacoesEnel")
    }

    # Criar lista final de reclamações sem referências circulares
    reclamacoes_completas = []
    for rec in reclamacoes:
        rec_id = rec[0]

        reclamacao_completa = {
            "motivo": dict(motivos.get(rec[1], {})),  
            "reclamante": dict(reclamantes.get(rec[2], {})),  
            "procurador": dict(procuradores.get(rec[3], {})) if rec[3] else {},  
            "titulo": rec[4],
            "situacao": rec[5],
            "caminho_dir": rec[6],
            "data_abertura": serialize_datetime(rec[7]),
            "ultima_mudanca": serialize_datetime(rec[8]),
            "criador": rec[9],
            "created_at": serialize_datetime(rec[10]),
            "reclamados": [dict(reclamados.get(rid, {})) for rid in relacao_dict.get(rec_id, [])],
            "reclamacoes_geral": dict(geral_dict.get(rec_id, {})),
            "reclamacoes_enel": dict(enel_dict.get(rec_id, {}))
        }
        reclamacoes_completas.append(reclamacao_completa)

    # Serializar JSON sem erro de referência circular
    return_json = orjson.dumps({"reclamacoes": reclamacoes_completas}, default=serialize_datetime).decode()

    print(f"[DB] {json.dumps(json.loads(return_json), indent=4)}")

    return return_json


def action_get_p_reclamacoes(request):
    import datetime
    
    limit = int(request.get("limit", 10))  
    offset = int(request.get("offset", 0))  
    
    query_reclamacoes = f"""
        SELECT * FROM Reclamacoes
        LIMIT {limit} OFFSET {offset}
    """
    reclamacoes = execute_query(query_reclamacoes)
    
    return aux_all_recl(request, reclamacoes)


def action_get_all_reclamacoes(request):
    reclamacoes = execute_query(QUERIES["get_all_reclamacoes"])
    
    return aux_all_recl(request, reclamacoes)


def action_update_situacao_reclamacao_por_titulo(request):
    titulo = request.get("titulo")
    situacao_new = request.get("situacao")
    print(titulo)
    print(situacao_new)
    reclamacao_id = execute_query(QUERIES["get_reclamacao_id_por_titulo"], (titulo,))[0][0]
    situacao_old = execute_query(QUERIES["get_reclamacao_situacao_por_titulo"], (titulo,))[0][0]

    execute_query(QUERIES["update_situacao_reclamacao_por_titulo"], (situacao_new, titulo))
    execute_query(QUERIES["insert_situacao_mudanca_historico"], (reclamacao_id, situacao_old, situacao_new))

    print(f"[DB] Situação da reclamação {titulo} atualizada com sucesso: {situacao_old} -> {situacao_new}")

    return {"status": "ok"}
    
   
def action_count_reclamacoes(request):
    quantidade = execute_query(QUERIES["count_reclamacoes"])

    print(f"[DB] Quantidade de reclamações: {quantidade[0][0]}")
    return {"count": quantidade[0][0]}


def action_count_reclamacoes_enel(request):
    quantidade = execute_query(QUERIES["count_reclamacoes_enel"])

    print(f"[DB] Quantidade de reclamações Enel: {quantidade[0][0]}")
    return {"count": quantidade[0][0]}


def action_count_reclamacoes_geral(request):
    quantidade = execute_query(QUERIES["count_reclamacoes_geral"])

    print(f"[DB] Quantidade de reclamações gerais: {quantidade[0][0]}")
    return {"count": quantidade[0][0]}


def action_get_reclamante_por_id(request):
    id = request.get("id")
    query = """
        SELECT reclamante_id, nome, rg, cpf, telefone, email FROM Reclamantes WHERE reclamante_id = (%s)
    """
    results = execute_query(query, (id,))

    print(f"[DB] Reclamante encontrado: {results[0] if results else None}")
    return {"reclamante": results[0] if results else None}


def action_get_reclamante_por_cpf(request):
    cpf = request.get("cpf")
    query = "SELECT reclamante_id, nome, rg, cpf, telefone, email FROM Reclamantes WHERE cpf = (%s)"
    results = execute_query(query, (cpf,))

    print(f"[DB] Reclamante encontrado: {results[0] if results else None}")
    return {"reclamante": results[0] if results else None}


def action_get_reclamante_por_rg(request):
    rg = request.get("rg")
    query = "SELECT reclamante_id, nome, rg, cpf, telefone, email FROM Reclamantes WHERE rg = (%s)"
    results = execute_query(query, (rg,))

    print(f"[DB] Reclamante encontrado: {results[0] if results else None}")
    return {"reclamante": results[0] if results else None}


def action_get_all_reclamantes(request):
    query = "SELECT reclamante_id, nome, rg, cpf, telefone, email FROM Reclamantes"
    results = execute_query(query)

    print(f"[DB] Reclamantes encontrados: {results}")
    return {"reclamantes": results}


def action_insert_reclamante(request):
    reclamante = request.get("reclamante")
    query = """
        INSERT INTO Reclamantes (nome, rg, cpf, telefone, email)
        VALUES ((%s), (%s), (%s), (%s), (%s))
    """
    execute_query(query, (reclamante["Nome"], reclamante["Rg"], reclamante["Cpf"], reclamante["Telefone"], reclamante["Email"]))

    print(f"[DB] Reclamante inserido com sucesso: {reclamante}")
    return {"status": "ok"}


def action_update_reclamante_por_id(request):
    id = request.get("id")
    reclamante = request.get("reclamante")
    query = """
        UPDATE Reclamantes
        SET nome = (%s), rg = (%s), cpf = (%s), telefone = (%s), email = (%s)
        WHERE reclamante_id = (%s)
    """
    execute_query(query, (reclamante["Nome"], reclamante["Rg"], reclamante["Cpf"], reclamante["Telefone"], reclamante["Email"], id))

    print(f"[DB] Reclamante atualizado com sucesso: {reclamante}")
    return {"status": "ok"}


def action_delete_reclamante_por_id(request):
    id = request.get("id")
    query = "DELETE FROM Reclamantes WHERE reclamante_id = (%s)"
    execute_query(query, (id,))

    print(f"[DB] Reclamante deletado com sucesso: {id}")
    return {"status": "ok"}


def action_count_reclamantes(request):
    results = execute_query(QUERIES["count_reclamantes"])

    print(f"[DB] Quantidade de reclamantes: {results[0][0]}")
    return {"count": results[0][0]}


def action_get_reclamado_por_id(request):
    id = request.get("id")
    query = """
        SELECT nome, cpf, cnpj, numero_addr, logradouro_addr, bairro_addr, cidade_addr, uf_addr, cep, telefone, email
        FROM Reclamados WHERE reclamado_id = (%s)
    """
    results = execute_query(query, (id,))

    print(f"[DB] Reclamado encontrado: {results[0] if results else None}")
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

    print(f"[DB] Reclamado inserido com sucesso: {reclamado}")
    return {"status": "ok"}

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
    return {"status": "ok"}


def action_delete_reclamado_por_id(request):
    id = request.get("id")
    query = "DELETE FROM Reclamados WHERE reclamado_id = (%s)"
    execute_query(query, (id,))
    return {"status": "ok"}


def action_get_all_reclamados(request):
    results = execute_query(QUERIES["get_all_reclamados"])
    return {"reclamados": results}


def action_count_reclamados(request):
    results = execute_query(QUERIES["count_reclamados"])
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


def action_get_motivo_id_por_nome(request):
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
    execute_query(QUERIES["insert_motivo"], (motivo["Nome"],))
    return {"status": "ok"}


def action_delete_motivo_por_nome(request):
    nome = request.get("nome")
    execute_query(QUERIES["delete_motivo_por_nome"], (nome,))
    return {"status": "ok"}


def action_update_motivo_por_id(request):
    nome = request.get("nome")
    novo_nome = request.get("novoNome")
    execute_query(QUERIES["update_motivo_por_id"], (novo_nome or nome, nome))
    return {"status": "ok"}


def action_count_motivos(request):
    results = execute_query(QUERIES["count_motivos"])
    return {"count": results[0][0]}


def action_estatistica_mais_reclamados(request):
    quantidade = request.get("quantidade", 5)
    print(quantidade)
    results = execute_query(QUERIES["estatistica_mais_reclamados"], (quantidade,))
    print(results)
    return {"reclamados": results}


def action_estatistica_reclamacoes_por_mes_ano_atual(request):
    query = QUERIES["estatistica_reclamacoes_por_mes_ano_atual"]
    
    resultados = execute_query(query) 

    estatisticas = {str(mes): 0 for mes in range(1, 13)}
    
    for mes, total in resultados:
        estatisticas[str(int(mes))] = total

    return {"estatisticas": estatisticas}


def action_estatistica_motivos_mais_usados(request):    
    resultados = execute_query(QUERIES["estatistica_motivos_mais_usados"])

    return {"estatisticas": resultados}


def action_estatistica_reclamacoes_por_criador(request):
    resultados = execute_query(QUERIES["estatistica_reclamacoes_por_criador"])

    return {"estatisticas": resultados}


def action_estatistica_reclamacoes_por_situacao(request):
    resultados = execute_query(QUERIES["estatistica_reclamacoes_por_situacao"])

    return {"estatisticas": resultados}


def action_get_all_usuarios(request):
    results = execute_query(QUERIES["get_all_usuarios"])

    return {"usuarios": results}


def action_insert_usuario(request):
    usuario = request.get("usuario")
    execute_query(QUERIES["insert_usuario"], (usuario["Nome"], usuario["Cargo"], usuario["HashSalt"], usuario["Salt"]))

    return {"status": "ok"}


def action_count_reclamacoes_geral_ano(request):
    quantidade = execute_query(QUERIES["count_reclamacoes_geral_ano"])

    return {"count": quantidade[0][0]}


def action_count_reclamacoes_enel_ano(request):
    quantidade = execute_query(QUERIES["count_reclamacoes_enel_ano"])

    return {"count": quantidade[0][0]}


def action_get_ultimas_cinco_reclamacoes(request):
    results = execute_query(QUERIES["get_ultimas_cinco_reclamacoes"])

    return {"reclamacoes": results}


QUERIES = {
    "get_reclamacao_id_por_titulo": "SELECT reclamacao_id FROM Reclamacoes WHERE titulo = (%s)",
    "get_reclamado_id_por_addr": "SELECT reclamado_id FROM Reclamados WHERE numero_addr = (%s) AND logradouro_addr = (%s) AND bairro_addr = (%s) AND cidade_addr = (%s) AND uf_addr = (%s) AND cep = (%s) LIMIT 1",
    "get_reclamado_id_por_cnpj": "SELECT reclamado_id FROM Reclamados WHERE cnpj = (%s)",
    "get_reclamacao_por_titulo": "SELECT * FROM reclamacoes where titulo = (%s)",
    "get_reclamante_por_cpf": "SELECT reclamante_id FROM Reclamantes WHERE cpf = (%s)",
    "get_procurador_por_cpf": "SELECT procurador_id FROM Procuradores WHERE cpf = (%s)",
    "get_reclamacao_situacao_por_titulo": "SELECT situacao FROM Reclamacoes WHERE titulo = (%s)",
    "get_motivo_id_por_nome": "SELECT motivo_id FROM Motivos WHERE nome = (%s)",
    "get_reclamante_id_por_cpf": "SELECT reclamante_id FROM Reclamantes WHERE cpf = (%s)",
    "get_all_reclamacoes": "SELECT * FROM Reclamacoes",
    "get_all_motivos": "SELECT * FROM Motivos",
    "get_all_procuradores": "SELECT * FROM Procuradores",
    "get_all_reclamados": "SELECT * FROM Reclamados",
    "get_all_reclamantes": "SELECT * FROM Reclamantes",
    "insert_reclamante": "INSERT INTO Reclamantes (nome, rg, cpf, telefone, email) VALUES (%s, %s, %s, %s, %s)",
    "insert_procurador": "INSERT INTO Procuradores (nome, rg, cpf, telefone, email) VALUES (%s, %s, %s, %s, %s)",
    "insert_relacao_reclamado_reclamacao": "INSERT INTO RelacaoProcessoReclamado (reclamacao_id, reclamado_id) VALUES (%s, %s)",
    "insert_reclamado": "INSERT INTO Reclamados (nome, cpf, cnpj, numero_addr, logradouro_addr, bairro_addr, cidade_addr, uf_addr, telefone, email, cep) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
    "insert_motivo": "INSERT INTO Motivos (nome) VALUES ((%s))",
    "insert_reclamacao": "INSERT INTO Reclamacoes (motivo_id, reclamante_id, procurador_id, titulo, situacao, caminho_dir, data_abertura, criador) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
    "insert_reclamacao_geral": "INSERT INTO ReclamacoesGeral (reclamacao_id, data_audiencia, conciliador) VALUES (%s, %s, %s)",
    "insert_reclamacao_enel": "INSERT INTO ReclamacoesEnel (reclamacao_id, atendente, contato_enel_telefone, contato_enel_email, observacao) VALUES (%s, %s, %s, %s, %s)",
    "insert_situacao_mudanca_historico": "INSERT INTO HistoricoMudancaSituacao (reclamacao_id, situacao_old, situacao_new) VALUES (%s, %s, %s)",
    "update_situacao_reclamacao_por_titulo": "UPDATE Reclamacoes SET situacao = (%s) WHERE titulo = (%s)",
    "delete_reclamacao_por_titulo": "DELETE FROM Reclamacoes WHERE titulo = (%s)",
    "delete_motivo_por_nome": "DELETE FROM Motivos WHERE nome = (%s)",
    "count_reclamacoes": "SELECT COUNT(*) FROM Reclamacoes",
    "count_reclamacoes_enel": "SELECT COUNT(*) FROM ReclamacoesEnel",
    "count_reclamacoes_geral": "SELECT COUNT(*) FROM ReclamacoesEnel",
    "count_reclamacoes_enel_ano": "SELECT SUM((DATE_PART('year', Reclamacoes.data_abertura) = DATE_PART('year', CURRENT_DATE))::int) FROM ReclamacoesEnel JOIN Reclamacoes ON ReclamacoesEnel.reclamacao_id = Reclamacoes.reclamacao_id",
    "count_reclamacoes_geral_ano": "SELECT SUM((DATE_PART('year', Reclamacoes.data_abertura) = DATE_PART('year', CURRENT_DATE))::int) FROM ReclamacoesGeral JOIN Reclamacoes ON ReclamacoesGeral.reclamacao_id = Reclamacoes.reclamacao_id",
    "count_reclamantes": "SELECT COUNT(*) FROM Reclamantes",
    "count_reclamados": "SELECT COUNT(*) FROM Reclamados",
    "count_motivos": "SELECT COUNT(*) FROM Motivos",
    "update_reclamacao_enel": "UPDATE ReclamacoesEnel SET atendente = COALESCE((%s), atendente), contato_enel_telefone = COALESCE((%s), contato_enel_telefone), contato_enel_email = COALESCE((%s), contato_enel_email), observacao = COALESCE((%s), observacao) WHERE reclamacao_id = (%s);",
    "update_reclamacao_geral": "UPDATE ReclamacoesGeral SET data_audiencia = COALESCE((%s), data_audiencia), conciliador = COALESCE((%s), conciliador) WHERE reclamacao_id = (%s);",
    "update_motivo_por_id": "UPDATE Motivos SET nome = (%s) WHERE nome = (%s)",
    "update_reclamacao": "UPDATE Reclamacoes SET motivo_id = (%s), reclamante_id = (%s), procurador_id = (%s), titulo = (%s), situacao = (%s), caminho_dir = (%s), data_abertura = (%s), ultima_mudanca = CURRENT_TIMESTAMP, criador = (%s) WHERE reclamacao_id = (%s);",
    "delete_reclamados_por_reclamacao": "DELETE FROM RelacaoProcessoReclamado WHERE reclamacao_id = %s;",
    "insert_relacao_reclamacao_reclamado": "INSERT INTO RelacaoProcessoReclamado (reclamacao_id, reclamado_id) VALUES (%s, %s);",
    "estatistica_mais_reclamados": "SELECT r.nome, COUNT(rpr.reclamacao_id) AS total_reclamacoes FROM RelacaoProcessoReclamado AS rpr JOIN Reclamados AS r ON rpr.reclamado_id = r.reclamado_id GROUP BY r.reclamado_id, r.nome ORDER BY total_reclamacoes DESC LIMIT (%s);",
    "estatistica_motivos_mais_usados": "SELECT m.nome AS motivo, COUNT(r.reclamacao_id) AS total_reclamacoes FROM Reclamacoes r JOIN Motivos m ON r.motivo_id = m.motivo_id GROUP BY m.nome ORDER BY total_reclamacoes DESC;",
    "estatistica_reclamacoes_por_mes_ano_atual": "SELECT EXTRACT(MONTH FROM data_abertura) AS mes, COUNT(reclamacao_id) AS total_reclamacoes FROM Reclamacoes WHERE EXTRACT(YEAR FROM data_abertura) = EXTRACT(YEAR FROM CURRENT_DATE) GROUP BY mes ORDER BY mes;",
    "estatistica_reclamacoes_por_mes_ano": "SELECT EXTRACT(MONTH FROM data_abertura) AS mes, COUNT(reclamacao_id) AS total_reclamacoes FROM Reclamacoes WHERE EXTRACT(YEAR FROM data_abertura) = (%s) GROUP BY mes ORDER BY mes;",
    "estatistica_cidades_com_mais_reclamacoes": "SELECT r.cidade_addr AS cidade, COUNT(rpr.reclamacao_id) AS total_reclamacoes FROM RelacaoProcessoReclamado AS rpr JOIN Reclamados AS r ON rpr.reclamado_id = r.reclamado_id GROUP BY r.cidade_addr ORDER BY total_reclamacoes DESC;",
    "insert_usuario": "INSERT INTO Usuarios (nome, cargo, hash_and_salt, salt) VALUES (%s, %s, %s, %s)",
    "get_usuario_por_nome": "SELECT * FROM Usuarios WHERE nome = (%s)",
    "get_detalhes_reclamacao_por_titulo": "SELECT r.*, m.nome AS motivo_nome, rc.nome AS reclamante_nome, p.nome AS procurador_nome FROM Reclamacoes r JOIN Motivos m ON r.motivo_id = m.motivo_id JOIN Reclamantes rc ON r.reclamante_id = rc.reclamante_id LEFT JOIN Procuradores p ON r.procurador_id = p.procurador_id WHERE r.titulo = (%s)",
    "get_reclamados_por_reclamacao_id": "SELECT rd.* FROM Reclamados rd JOIN RelacaoProcessoReclamado rpr ON rd.reclamado_id = rpr.reclamado_id WHERE rpr.reclamacao_id = (%s)",
    "get_historico_situacao_por_reclamacao_id": "SELECT * FROM HistoricoMudancaSituacao WHERE reclamacao_id = (%s) ORDER BY changed_at DESC",
    "get_reclamacao_geral_por_id": "SELECT * FROM ReclamacoesGeral WHERE reclamacao_id = (%s)",
    "get_reclamacao_enel_por_id": "SELECT * FROM ReclamacoesEnel WHERE reclamacao_id = (%s)",
    "check_titulo_existe": "SELECT EXISTS(SELECT 1 FROM Reclamacoes WHERE titulo = (%s))",
    "estatistica_reclamacoes_por_criador": "SELECT criador, COUNT(*) AS total FROM Reclamacoes GROUP BY criador ORDER BY total DESC",
    "estatistica_reclamacoes_por_situacao": "SELECT situacao, COUNT(*) AS total FROM Reclamacoes GROUP BY situacao ORDER BY total DESC",
    "get_all_usuarios": "SELECT nome, cargo FROM Usuarios",
    "update_usuario_hash": "UPDATE Usuarios SET hash_and_salt = (%s), salt = (%s) WHERE nome = (%s)",
    "delete_usuario_por_id": "DELETE FROM Usuarios WHERE usuario_id = (%s)",
    "get_ultimas_cinco_reclamacoes_criadas": "SELECT titulo, situacao FROM Reclamacoes ORDER BY created_at DESC LIMIT 5"
}

ACTIONS = {
    "insert_reclamacao": action_insert_reclamacao,
    "delete_reclamacao_por_titulo": action_delete_reclamacao_por_titulo,
    "get_all_reclamacoes": action_get_all_reclamacoes,
    "get_p_reclamacoes": action_get_p_reclamacoes,
    "get_reclamacao_por_titulo": action_get_reclamacao_por_titulo,
    "update_situacao_reclamacao_por_titulo": action_update_situacao_reclamacao_por_titulo,
    "update_reclamacao": action_update_reclamacao,
    "count_reclamacoes": action_count_reclamacoes,
    "count_reclamacoes_enel": action_count_reclamacoes_enel,
    "count_reclamacoes_geral": action_count_reclamacoes_geral,
    "get_reclamante_por_id": action_get_reclamante_por_id,
    "get_reclamante_por_cpf": action_get_reclamante_por_cpf,
    "get_reclamante_por_rg": action_get_reclamante_por_rg,
    "get_all_reclamantes": action_get_all_reclamantes,
    "get_all_usuarios": action_get_all_usuarios,
    "insert_reclamante": action_insert_reclamante,
    "update_reclamante_por_id": action_update_reclamante_por_id,
    "delete_reclamante_por_id": action_delete_reclamante_por_id,
    "count_reclamantes": action_count_reclamantes,
    "get_reclamado_por_id": action_get_reclamado_por_id,
    "insert_reclamado": action_insert_reclamado,
    "update_reclamado_por_id": action_update_reclamado_por_id,
    "delete_reclamado_por_id": action_delete_reclamado_por_id,
    "get_all_reclamados": action_get_all_reclamados,
    "count_reclamados": action_count_reclamados,
    "get_motivo_por_nome": action_get_motivo_por_nome,
    "get_motivo_por_id": action_get_motivo_por_id,
    "get_motivo_id_por_nome": action_get_motivo_id_por_nome,
    "get_all_motivos": action_get_all_motivos,
    "insert_motivo": action_insert_motivo,
    "delete_motivo_por_nome": action_delete_motivo_por_nome,
    "update_motivo_por_id": action_update_motivo_por_id,
    "count_motivos": action_count_motivos,
    "estatistica_mais_reclamados": action_estatistica_mais_reclamados,
    "estatistica_motivos_mais_usados": action_estatistica_motivos_mais_usados,
    "estatistica_reclamacoes_por_mes_ano_atual": action_estatistica_reclamacoes_por_mes_ano_atual,
    "insert_usuario": action_insert_usuario,
    "estatistica_reclamacoes_por_criador": action_estatistica_reclamacoes_por_criador,
    "estatistica_reclamacoes_por_situacao": action_estatistica_reclamacoes_por_situacao,
    "count_reclamacoes_enel_ano": action_count_reclamacoes_enel_ano,
    "count_reclamacoes_geral_ano": action_count_reclamacoes_geral_ano,
    "get_ultimas_cinco_reclamacoes": action_get_ultimas_cinco_reclamacoes
}
