CREATE TABLE Reclamados(
    reclamado_id INT PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    nome VARCHAR(150) NOT NULL,
    cpf CHAR(11) UNIQUE,
    cnpj CHAR(14) UNIQUE,
    numero_addr SMALLINT NOT NULL,
    logradouro_addr VARCHAR(100) NOT NULL,
    bairro_addr VARCHAR(100) NOT NULL,
    cidade_addr VARCHAR(100) NOT NULL,
    uf_addr CHAR(2) NOT NULL,
    telefone CHAR(11),
    email VARCHAR(100) CHECK (email IS NULL OR email LIKE '%_@__%.__%'),
    cep CHAR(8) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Usuarios(
    usuario_id INT PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    nome VARCHAR(100) NOT NULL,
    cargo VARCHAR(30) NOT NULL,
    hash_and_salt VARCHAR(100) NOT NULL,
    salt VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Motivos(
    motivo_id INT PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    nome VARCHAR(75) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Reclamantes(
    reclamante_id INT PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    nome VARCHAR(100) NOT NULL,
    rg VARCHAR(10) UNIQUE,
    cpf CHAR(11) NOT NULL UNIQUE,
    telefone CHAR(11),
    email VARCHAR(100) CHECK (email IS NULL OR email LIKE '%_@__%.__%'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Procuradores(
    procurador_id INT PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    nome VARCHAR(100) NOT NULL,
    rg VARCHAR(10) UNIQUE,
    cpf CHAR(11) NOT NULL UNIQUE,
    telefone CHAR(11),
    email VARCHAR(100) CHECK (email IS NULL OR email LIKE '%_@__%.__%'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Reclamacoes(
    reclamacao_id INT PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    motivo_id INT NOT NULL,
    reclamante_id INT NOT NULL,
    procurador_id INT,
    titulo VARCHAR(10) NOT NULL UNIQUE,
    situacao VARCHAR(75) NOT NULL,
    caminho_dir VARCHAR(200) NOT NULL UNIQUE,
    data_abertura DATE NOT NULL,
    ultima_mudanca TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    criador VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (reclamante_id) REFERENCES Reclamantes(reclamante_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (motivo_id) REFERENCES Motivos(motivo_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (procurador_id) REFERENCES Procuradores(procurador_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE ReclamacoesGeral(
    reclamacao_id INT NOT NULL,
    data_audiencia TIMESTAMP,
    conciliador VARCHAR(100),

    FOREIGN KEY (reclamacao_id) REFERENCES Reclamacoes(reclamacao_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE ReclamacoesEnel(
    reclamacao_id INT NOT NULL,
    atendente VARCHAR(100),
    contato_enel_telefone CHAR(11),
    contato_enel_email VARCHAR(100) CHECK (contato_enel_email IS NULL OR contato_enel_email LIKE '%_@__%.__%'),
    observacao TEXT,

    FOREIGN KEY (reclamacao_id) REFERENCES Reclamacoes(reclamacao_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE RelacaoProcessoReclamado(
    reclamacao_id INT NOT NULL,
    reclamado_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (reclamacao_id) REFERENCES Reclamacoes(reclamacao_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (reclamado_id) REFERENCES Reclamados(reclamado_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE HistoricoMudancaSituacao(
    reclamacao_id INT,
    situacao_old VARCHAR(50),
    situacao_new VARCHAR(50) NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (reclamacao_id) REFERENCES Reclamacoes(reclamacao_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);