CREATE TABLE Reclamados(
    reclamado_id INT PRIMARY KEY NOT NULL IDENTITY(1, 1),
    nome NVARCHAR(150) NOT NULL,
    cpf NCHAR(11) NULL UNIQUE,
    cnpj NCHAR(14) NULL UNIQUE,
    numero_addr SMALLINT NOT NULL,
    logradouro_addr NVARCHAR(100) NOT NULL,
    bairro_addr NVARCHAR(100) NOT NULL,
    cidade_addr NVARCHAR(100) NOT NULL,
    uf_addr NCHAR(2) NOT NULL,
    telefone NCHAR(11) NULL,
    email NVARCHAR(100) NULL CHECK (email IS NULL OR email LIKE '%_@__%.__%'),
    cep NCHAR(8) NOT NULL,
    created_at DATETIME DEFAULT GETDATE()
);

CREATE TABLE Usuarios(
    usuario_id INT PRIMARY KEY NOT NULL IDENTITY(1, 1),
    nome NVARCHAR(100) NOT NULL,
    cargo NVARCHAR(30) NOT NULL,
    hash_and_salt NVARCHAR(100) NOT NULL,
    salt NVARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT GETDATE()
);

CREATE TABLE Motivos(
    motivo_id INT PRIMARY KEY NOT NULL IDENTITY(1, 1),
    nome NVARCHAR(75) NOT NULL UNIQUE,
    created_at DATETIME DEFAULT GETDATE(),
);

CREATE TABLE Reclamantes(
    reclamante_id INT PRIMARY KEY NOT NULL IDENTITY(1, 1),
    nome NVARCHAR(100) NOT NULL,
    rg NVARCHAR(10) NULL UNIQUE,
    cpf NCHAR(11) NOT NULL UNIQUE,
    telefone NCHAR(11) NULL,
    email NVARCHAR(100) NULL CHECK (email IS NULL OR email LIKE '%_@__%.__%'),
    created_at DATETIME DEFAULT GETDATE(),
);

CREATE TABLE Procuradores(
    procurador_id INT PRIMARY KEY NOT NULL IDENTITY(1, 1),
    nome NVARCHAR(100) NOT NULL,
    rg NVARCHAR(10) NULL UNIQUE,
    cpf NCHAR(11) NOT NULL UNIQUE,
    telefone NCHAR(11) NULL,
    email NVARCHAR(100) NULL CHECK (email IS NULL OR email LIKE '%_@__%.__%'),
    created_at DATETIME DEFAULT GETDATE(),
);

CREATE TABLE Reclamacoes(
    reclamacao_id INT PRIMARY KEY NOT NULL IDENTITY(1, 1),
    motivo_id INT NOT NULL,
    reclamante_id INT NOT NULL,
    procurador_id INT NULL,
    titulo NVARCHAR(10) NOT NULL UNIQUE,
    situacao NVARCHAR(75) NOT NULL,
    caminho_dir NVARCHAR(200) NOT NULL UNIQUE,
    data_abertura DATE NOT NULL,
    ultima_mudanca DATETIME DEFAULT GETDATE(),
    created_at DATETIME DEFAULT GETDATE(),

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
    data_audiencia DATETIME NULL,
    conciliador NVARCHAR(100) NULL,

    FOREIGN KEY (reclamacao_id) REFERENCES Reclamacoes(reclamacao_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,    
);

CREATE TABLE ReclamacoesEnel(
    reclamacao_id INT NOT NULL,
    atendente NVARCHAR(100) NULL,
    contato_enel_telefone NCHAR(11) NULL,
    contato_enel_email NVARCHAR(100) NULL CHECK (contato_enel_email IS NULL OR contato_enel_email LIKE '%_@__%.__%'),
    observacao TEXT NULL,

    FOREIGN KEY (reclamacao_id) REFERENCES Reclamacoes(reclamacao_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,    
);

CREATE TABLE RelacaoProcessoReclamado(
    reclamacao_id INT NOT NULL,
    reclamado_id INT NULL,
    created_at DATETIME DEFAULT GETDATE(),

    FOREIGN KEY (reclamacao_id) REFERENCES Reclamacoes(reclamacao_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (reclamado_id) REFERENCES Reclamados(reclamado_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
);

CREATE TABLE HistoricoMudancaSituacao(
    reclamacao_id INT,
    situacao_old NVARCHAR(50) NULL,
    situacao_new NVARCHAR(50) NOT NULL,
    changed_at DATETIME DEFAULT GETDATE(),

    FOREIGN KEY (reclamacao_id) REFERENCES Reclamacoes(reclamacao_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
);
