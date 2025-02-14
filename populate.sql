-------------------------------
-- 1. Inserir dados na tabela Motivos
-------------------------------
INSERT INTO Motivos (nome) VALUES
  ('Cobrança Indevida'),
  ('Má qualidade do serviço'),
  ('Atendimento Ruim'),
  ('Erro na fatura'),
  ('Falta de transparência')
ON CONFLICT DO NOTHING;

-------------------------------
-- 2. Inserir dados na tabela Reclamantes
-------------------------------
INSERT INTO Reclamantes (nome, rg, cpf, telefone, email) VALUES
  ('João Silva', '123456789', '11111111111', '11999990001', 'joao.silva@exemplo.com'),
  ('Maria Souza', '987654321', '22222222222', '11999990002', 'maria.souza@exemplo.com'),
  ('Pedro Oliveira', '555555555', '33333333333', '11999990003', 'pedro.oliveira@exemplo.com'),
  ('Ana Paula', '111223344', '44444444444', '11999990004', 'anapaula@exemplo.com'),
  ('Carlos Mendes', '556677889', '55555555555', '11999990005', 'carlos.mendes@exemplo.com')
ON CONFLICT DO NOTHING;

-------------------------------
-- 3. Inserir dados na tabela Procuradores
-------------------------------
INSERT INTO Procuradores (nome, rg, cpf, telefone, email) VALUES
  ('Advogado A', '112233445', '44444444444', '11988887777', 'adv.a@exemplo.com'),
  ('Advogado B', '556677889', '55555555555', '11988887778', 'adv.b@exemplo.com'),
  ('Advogado C', '998877665', '66666666666', '11988887779', 'adv.c@exemplo.com')
ON CONFLICT DO NOTHING;

-------------------------------
-- 4. Inserir dados na tabela Reclamados (empresas)
-------------------------------
INSERT INTO Reclamados (nome, cnpj, numero_addr, logradouro_addr, bairro_addr, cidade_addr, uf_addr, telefone, email, cep)
VALUES
  ('Empresa A', '12345678901234', 100, 'Rua A', 'Bairro A', 'Cidade A', 'SP', '1133224455', 'contato@empresaA.com', '01001000'),
  ('Empresa B', '98765432109876', 200, 'Avenida B', 'Bairro B', 'Cidade B', 'RJ', '2233224455', 'contato@empresaB.com', '20020000'),
  ('Empresa C', '19283746509123', 300, 'Praça C', 'Bairro C', 'Cidade C', 'MG', '3333224455', 'contato@empresaC.com', '30130000'),
  ('Empresa D', '56473829105678', 400, 'Alameda D', 'Bairro D', 'Cidade D', 'RS', '4433224455', 'contato@empresaD.com', '90090000')
ON CONFLICT DO NOTHING;

-------------------------------
-- 5. Inserir dados na tabela Usuarios (usuários do sistema)
-------------------------------
INSERT INTO Usuarios (nome, cargo, hash_and_salt, salt) VALUES
  ('Usuario Admin', 'Administrador', 'hash123', 'salt123'),
  ('Usuario Operador', 'Operador', 'hash456', 'salt456')
ON CONFLICT DO NOTHING;

-------------------------------
-- 6. Inserir dados na tabela Reclamacoes
-------------------------------
-- Cada linha utiliza subconsultas para escolher um motivo, reclamante e (quando necessário) procurador de forma aleatória.
INSERT INTO Reclamacoes 
  (motivo_id, reclamante_id, procurador_id, titulo, situacao, caminho_dir, data_abertura, ultima_mudanca, criador)
VALUES
  -- Reclamação 1: Tipo Geral (sem procurador)
  (
    (SELECT motivo_id FROM Motivos ORDER BY random() LIMIT 1),
    (SELECT reclamante_id FROM Reclamantes ORDER BY random() LIMIT 1),
    NULL,
    'G001/2025',
    'Em tramitação: aguardando fazer notificação',
    '/home/~/recl/G001/2025',
    '2025-02-10',
    '2025-02-10',
    'Criador 1'
  ),
  -- Reclamação 2: Tipo Enel (com procurador)
  (
    (SELECT motivo_id FROM Motivos ORDER BY random() LIMIT 1),
    (SELECT reclamante_id FROM Reclamantes ORDER BY random() LIMIT 1),
    (SELECT procurador_id FROM Procuradores ORDER BY random() LIMIT 1),
    'E002/2025',
    'Em tramitação: aguardando envio da notificação',
    '/home/~/recl/E002/2025',
    '2025-02-11',
    '2025-02-12',
    'Criador 2'
  ),
  -- Reclamação 3: Tipo Geral (sem procurador)
  (
    (SELECT motivo_id FROM Motivos ORDER BY random() LIMIT 1),
    (SELECT reclamante_id FROM Reclamantes ORDER BY random() LIMIT 1),
    NULL,
    'G003/2025',
    'Em tramitação: aguardando realização da audiência',
    '/home/~/recl/G003/2025',
    '2025-02-09',
    '2025-02-13',
    'Criador 1'
  ),
  -- Reclamação 4: Tipo Enel (com procurador)
  (
    (SELECT motivo_id FROM Motivos ORDER BY random() LIMIT 1),
    (SELECT reclamante_id FROM Reclamantes ORDER BY random() LIMIT 1),
    (SELECT procurador_id FROM Procuradores ORDER BY random() LIMIT 1),
    'E004/2025',
    'Em tramitação: aguardando análise do processo',
    '/home/~/recl/E004/2025',
    '2025-02-14',
    '2025-02-15',
    'Criador 3'
  ),
  -- Reclamação 5: Tipo Geral (sem procurador)
  (
    (SELECT motivo_id FROM Motivos ORDER BY random() LIMIT 1),
    (SELECT reclamante_id FROM Reclamantes ORDER BY random() LIMIT 1),
    NULL,
    'G005/2025',
    'Em tramitação: aguardando retorno do setor responsável',
    '/home/~/recl/G005/2025',
    '2025-02-16',
    '2025-02-16',
    'Criador 2'
  ),
  -- Reclamação 6: Tipo Enel (com procurador)
  (
    (SELECT motivo_id FROM Motivos ORDER BY random() LIMIT 1),
    (SELECT reclamante_id FROM Reclamantes ORDER BY random() LIMIT 1),
    (SELECT procurador_id FROM Procuradores ORDER BY random() LIMIT 1),
    'E006/2025',
    'Em tramitação: aguardando encaminhamento para audiência',
    '/home/~/recl/E006/2025',
    '2025-02-17',
    '2025-02-18',
    'Criador 1'
  )
ON CONFLICT DO NOTHING;

-------------------------------
-- 7. Inserir dados na tabela ReclamacoesGeral
-------------------------------
-- Insere registros para reclamações de tipo Geral (títulos iniciados com "G")
INSERT INTO ReclamacoesGeral (reclamacao_id, data_audiencia, conciliador)
VALUES
  (
    (SELECT reclamacao_id FROM Reclamacoes WHERE titulo LIKE 'G%' ORDER BY random() LIMIT 1),
    '2025-02-20 09:00:00',
    'Conciliador 1'
  ),
  (
    (SELECT reclamacao_id FROM Reclamacoes WHERE titulo LIKE 'G%' ORDER BY random() LIMIT 1),
    '2025-02-21 11:00:00',
    'Conciliador 2'
  ),
  (
    (SELECT reclamacao_id FROM Reclamacoes WHERE titulo LIKE 'G%' ORDER BY random() LIMIT 1),
    '2025-02-22 14:00:00',
    'Conciliador 3'
  )
ON CONFLICT DO NOTHING;

-------------------------------
-- 8. Inserir dados na tabela ReclamacoesEnel
-------------------------------
-- Insere registros para reclamações de tipo Enel (títulos iniciados com "E")
INSERT INTO ReclamacoesEnel (reclamacao_id, atendente, contato_enel_telefone, contato_enel_email, observacao)
VALUES
  (
    (SELECT reclamacao_id FROM Reclamacoes WHERE titulo LIKE 'E%' ORDER BY random() LIMIT 1),
    'Atendente 1',
    '11977776666',
    'atendente1@enel.com',
    'Observação de atendimento Enel 1'
  ),
  (
    (SELECT reclamacao_id FROM Reclamacoes WHERE titulo LIKE 'E%' ORDER BY random() LIMIT 1),
    'Atendente 2',
    '11977776667',
    'atendente2@enel.com',
    'Observação de atendimento Enel 2'
  )
ON CONFLICT DO NOTHING;

-------------------------------
-- 9. Inserir dados na tabela RelacaoProcessoReclamado
-------------------------------
-- Associa reclamações a empresas (Reclamados) escolhidos aleatoriamente
INSERT INTO RelacaoProcessoReclamado (reclamacao_id, reclamado_id)
VALUES
  (
    (SELECT reclamacao_id FROM Reclamacoes ORDER BY random() LIMIT 1),
    (SELECT reclamado_id FROM Reclamados ORDER BY random() LIMIT 1)
  ),
  (
    (SELECT reclamacao_id FROM Reclamacoes ORDER BY random() LIMIT 1),
    (SELECT reclamado_id FROM Reclamados ORDER BY random() LIMIT 1)
  ),
  (
    (SELECT reclamacao_id FROM Reclamacoes ORDER BY random() LIMIT 1),
    (SELECT reclamado_id FROM Reclamados ORDER BY random() LIMIT 1)
  ),
  (
    (SELECT reclamacao_id FROM Reclamacoes ORDER BY random() LIMIT 1),
    (SELECT reclamado_id FROM Reclamados ORDER BY random() LIMIT 1)
  ),
  (
    (SELECT reclamacao_id FROM Reclamacoes ORDER BY random() LIMIT 1),
    (SELECT reclamado_id FROM Reclamados ORDER BY random() LIMIT 1)
  )
ON CONFLICT DO NOTHING;

-------------------------------
-- 10. Inserir dados na tabela HistoricoMudancaSituacao
-------------------------------
-- Registra diversas transições de situação para reclamações aleatórias
INSERT INTO HistoricoMudancaSituacao (reclamacao_id, situacao_old, situacao_new, changed_at)
VALUES
  (
    (SELECT reclamacao_id FROM Reclamacoes ORDER BY random() LIMIT 1),
    'Em tramitação: aguardando fazer notificação',
    'Em tramitação: aguardando envio da notificação',
    '2025-02-11 09:00:00'
  ),
  (
    (SELECT reclamacao_id FROM Reclamacoes ORDER BY random() LIMIT 1),
    'Em tramitação: aguardando envio da notificação',
    'Em tramitação: aguardando realização da audiência',
    '2025-02-13 14:30:00'
  ),
  (
    (SELECT reclamacao_id FROM Reclamacoes ORDER BY random() LIMIT 1),
    'Em tramitação: aguardando envio da notificação',
    'Em tramitação: aguardando análise do processo',
    '2025-02-14 10:30:00'
  ),
  (
    (SELECT reclamacao_id FROM Reclamacoes ORDER BY random() LIMIT 1),
    'Em tramitação: aguardando análise do processo',
    'Em tramitação: aguardando retorno do setor responsável',
    '2025-02-16 12:00:00'
  ),
  (
    (SELECT reclamacao_id FROM Reclamacoes ORDER BY random() LIMIT 1),
    'Em tramitação: aguardando retorno do setor responsável',
    'Em tramitação: aguardando encaminhamento para audiência',
    '2025-02-17 15:00:00'
  )
ON CONFLICT DO NOTHING;
