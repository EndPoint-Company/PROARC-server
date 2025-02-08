import datetime
import socket
import psycopg2
import json
import global_config
import global_config


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
    print(reclamacao)
    if reclamacao["Motivo"] == None:
        return {"status": "faltando motivo"}  
    if reclamacao["Reclamante"] == None:
        return {"status":"faltando reclamante"} 
    if reclamacao["Reclamados"] == None:
        return {"status":"faltando reclamado"}
    motivo_nome = reclamacao["Motivo"]["Nome"]
    motivo_id = execute_query(QUERIES["get_motivo_id_por_nome"], (motivo_nome,))[0][0]
    print(motivo_id)

    reclamante_cpf = reclamacao["Reclamante"]["Cpf"]
    reclamante_id = execute_query(QUERIES["get_reclamante_por_cpf"], (reclamante_cpf,))[0]
    if reclamante_id == None:
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
    
    print("maconha")   
    procurador_id = None
    if reclamacao["Procurador"] in reclamacao:
        procurador_cpf = reclamacao["Procurador"]["Cpf"]
        procurador_id = execute_query(QUERIES["get_procurador_por_cpf"], (procurador_cpf,))[0]
        if procurador_id[0][0] == None:
            execute_query(QUERIES["insert_procurador"], (reclamacao["Procurador"]["Nome"], reclamacao["Procurador"]["Rg"], reclamacao["Procurador"]["Cpf"], reclamacao["Procurador"]["Telefone"], reclamacao["Procurador"]["Email"]))
        procurador_id = execute_query(QUERIES["get_procurador_por_cpf"], (procurador_cpf,))[0][0]

    reclamados_ids = []
    print(procurador_id)
    for i in range(len(reclamacao["Reclamados"])):
        reclamado = reclamacao["Reclamados"][i]
        print(reclamado)
        reclamado_id = execute_query(QUERIES["get_reclamado_id_por_addr"], (reclamado["Numero"], reclamado["Logradouro"], reclamado["Bairro"], reclamado["Cidade"], reclamado["Uf"], reclamado["Cep"]))[0]
        print(reclamado_id)
        if reclamado_id == None:
            execute_query(QUERIES["insert_reclamado"], (reclamado["Nome"], reclamado["Cpf"], reclamado["Cnpj"], reclamado["Numero"], reclamado["Logradouro"], reclamado["Bairro"], reclamado["Cidade"], reclamado["Uf"], reclamado["Telefone"], reclamado["Email"], reclamado["Cep"]))
        reclamado_id = execute_query(QUERIES["get_reclamado_id_por_addr"], (reclamado["Numero"], reclamado["Logradouro"], reclamado["Bairro"], reclamado["Cidade"], reclamado["Uf"], reclamado["Cep"]))[0][0]
        reclamados_ids.append(reclamado_id)
    print(reclamados_ids)
    execute_query(QUERIES["insert_reclamacao"], (motivo_id, reclamante_id, procurador_id, reclamacao["Titulo"], reclamacao["Situacao"], reclamacao["CaminhoDir"], reclamacao["DataAbertura"], reclamacao["Criador"]))

    reclamacao_id = execute_query(QUERIES["get_reclamacao_id_por_titulo"], (reclamacao["Titulo"],))[0][0]
    print(reclamacao_id)
    for i in range(len(reclamados_ids)):
        execute_query(QUERIES["insert_relacao_reclamado_reclamacao"], (reclamacao_id, reclamados_ids[i]))

    if reclamacao["DataAudiencia"] in reclamacao:
        # todo o negocio de reclamacao geral
        execute_query(QUERIES["insert_reclamacao_geral"], (reclamacao_id, reclamacao["DataAudiencia"], reclamacao["Conciliador"]))
    if reclamacao["Observacao"] in reclamacao:
        # todo o negocio de reclamacao enel
        execute_query(QUERIES["insert_reclamacao_enel"], (reclamacao_id, reclamacao["Atendente"], reclamacao["ContatoEnelTelefone"], reclamacao["ContatoEnelEmail"], reclamacao["Observacao"]))

    return {"status": "ok"}


QUERIES = {
    "get_reclamacao_id_por_titulo": "SELECT reclamacao_id FROM Reclamacoes WHERE titulo = (%s)",
    "get_reclamado_id_por_addr": "SELECT reclamado_id FROM Reclamados WHERE numero_addr = (%s) AND logradouro_addr = (%s) AND bairro_addr = (%s) AND cidade_addr = (%s) AND uf_addr = (%s) AND cep = (%s)",
    "get_reclamado_id_por_cnpj": "SELECT reclamado_id FROM Reclamados WHERE cnpj = (%s)",
    "get_reclamante_por_cpf": "SELECT reclamante_id FROM Reclamantes WHERE cpf = (%s)",
    "get_procurador_por_cpf": "SELECT procurador_id FROM Procuradores WHERE cpf = (%s)",
    "insert_reclamante": "INSERT INTO Reclamantes (nome, rg, cpf, telefone, email) VALUES (%s, %s, %s, %s, %s)",
    "insert_relacao_reclamado_reclamacao": "INSERT INTO RelacaoProcessoReclamado (reclamacao_id, reclamado_id) VALUES (%s, %s)",
    "insert_reclamado": "INSERT INTO Reclamados (nome, cpf, cnpj, numero_addr, logradouro_addr, bairro_addr, cidade_addr, uf_addr, telefone, email, cep) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
    "insert_reclamacao": "INSERT INTO Reclamacoes (motivo_id, reclamante_id, procurador_id, titulo, situacao, caminho_dir, data_abertura, criador) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
    "insert_reclamacao_geral": "INSERT INTO ReclamacoesGeral (reclamacao_id, data_audiencia, conciliador) VALUES (%s, %s, %s)",
    "insert_reclamacao_enel": "INSERT INTO ReclamacoesEnel (reclamacao_id, atendente, contato_enel_telefone, contato_enel_email, observacao) VALUES (%s, %s, %s, %s, %s)",
    "get_motivo_id_por_nome": "SELECT motivo_id FROM Motivos WHERE nome = (%s)",
    "get_reclamante_id_por_cpf": "SELECT reclamante_id FROM Reclamantes WHERE cpf = (%s)",
}

ACTIONS = {
    "insert_reclamacao": action_insert_reclamacao,
}