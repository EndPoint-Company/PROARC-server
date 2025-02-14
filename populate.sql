-- 1. Inserir dados na tabela Motivos
INSERT INTO Motivos (nome) VALUES
  ('Cobrança Indevida'),
  ('Má qualidade do serviço'),
  ('Atendimento Ruim');

-- 2. Inserir dados na tabela Reclamantes
INSERT INTO Reclamantes (nome, rg, cpf, telefone, email) VALUES
  ('João Silva', '123456789', '11111111111', '11999990001', 'joao.silva@exemplo.com'),
  ('Maria Souza', '987654321', '22222222222', '11999990002', 'maria.souza@exemplo.com'),
  ('Pedro Oliveira', '555555555', '33333333333', '11999990003', 'pedro.oliveira@exemplo.com');

-- 3. Inserir dados na tabela Procuradores
INSERT INTO Procuradores (nome, rg, cpf, telefone, email) VALUES
  ('Advogado A', '112233445', '44444444444', '11988887777', 'adv.a@exemplo.com'),
  ('Advogado B', '556677889', '55555555555', '11988887778', 'adv.b@exemplo.com');

-- 4. Inserir dados na tabela Reclamados (empresas)
INSERT INTO Reclamados (nome, cnpj, numero_addr, logradouro_addr, bairro_addr, cidade_addr, uf_addr, telefone, email, cep)
VALUES
  ('Empresa A', '12345678901234', 100, 'Rua A', 'Bairro A', 'Cidade A', 'SP', '1133224455', 'contato@empresaA.com', '01001000'),
  ('Empresa B', '98765432109876', 200, 'Avenida B', 'Bairro B', 'Cidade B', 'RJ', '2233224455', 'contato@empresaB.com', '20020000'),
  ('Empresa C', '19283746509123', 300, 'Praça C', 'Bairro C', 'Cidade C', 'MG', '3333224455', 'contato@empresaC.com', '30130000');

-- 5. Inserir dados na tabela Usuarios (usuários do sistema)
INSERT INTO Usuarios (nome, cargo, hash_and_salt, salt) VALUES
  ('Usuario Admin', 'Administrador', 'hash123', 'salt123'),
  ('Usuario Operador', 'Operador', 'hash456', 'salt456');

-- 6. Inserir dados na tabela Reclamacoes  
-- Utilizando subconsultas para referenciar IDs aleatórios já existentes nas tabelas de apoio
INSERT INTO Reclamacoes 
  (motivo_id, reclamante_id, procurador_id, titulo, situacao, caminho_dir, data_abertura, ultima_mudanca, criador)
VALUES
  -- Reclamação 1: Tipo Geral (sem procurador), título "G001/2025"
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
  -- Reclamação 2: Tipo Enel, título "E002/2025"
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
  -- Reclamação 3: Tipo Geral (sem procurador), título "G003/2025"
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
  );

-- 7. Inserir dados na tabela ReclamacoesGeral  
-- Seleciona aleatoriamente uma reclamação do tipo Geral (título iniciando com 'G')
INSERT INTO ReclamacoesGeral (reclamacao_id, data_audiencia, conciliador)
VALUES
  (
    (SELECT reclamacao_id FROM Reclamacoes WHERE titulo LIKE 'G%' ORDER BY random() LIMIT 1),
    '2025-02-15 10:00:00',
    'Conciliador 1'
  );

-- 8. Inserir dados na tabela ReclamacoesEnel  
-- Seleciona aleatoriamente uma reclamação do tipo Enel (título iniciando com 'E')
INSERT INTO ReclamacoesEnel (reclamacao_id, atendente, contato_enel_telefone, contato_enel_email, observacao)
VALUES
  (
    (SELECT reclamacao_id FROM Reclamacoes WHERE titulo LIKE 'E%' ORDER BY random() LIMIT 1),
    'Atendente 1',
    '11977776666',
    'atendente@enel.com',
    'Observação de atendimento Enel'
  );

-- 9. Inserir dados na tabela RelacaoProcessoReclamado  
-- Associa aleatoriamente reclamações e empresas (Reclamados)
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
  );

-- 10. Inserir dados na tabela HistoricoMudancaSituacao  
-- Registra mudanças de situação utilizando reclamações selecionadas aleatoriamente
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
    'Em tramitação: aguardando realização da audiência',
    '2025-02-13 16:00:00'
  );
