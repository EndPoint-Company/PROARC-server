CREATE TABLE Reclamados(
    reclamado_id INT PRIMARY KEY NOT NULL IDENTITY(1, 1),
    nome NVARCHAR(150) NOT NULL,
    cpf NCHAR(11) NULL,
    cnpj NCHAR(14) NULL,
    numero_rua SMALLINT NULL,
    email NVARCHAR(150) NULL CONSTRAINT chk_email CHECK (email like '%_@__%.__%'),
    rua NVARCHAR(110) NULL,
    bairro NVARCHAR(100) NULL,
    cidade NVARCHAR(100) NULL,
    uf NCHAR(2) NULL,
    created_at DATETIME DEFAULT GETDATE()
);

CREATE TABLE Usuarios(
    usuario_id INT PRIMARY KEY NOT NULL IDENTITY(1, 1),
    nome NVARCHAR(50) NOT NULL,
    nivel_permissao SMALLINT NOT NULL CONSTRAINT digito_unico CHECK (nivel_permissao BETWEEN 0 and 4),
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
    rg NVARCHAR(20) NOT NULL,
    cpf NCHAR(11) NULL,
    created_at DATETIME DEFAULT GETDATE(),
);

CREATE TABLE ProcessosAdministrativos(
    processo_id INT PRIMARY KEY NOT NULL IDENTITY(1, 1),
    motivo_id INT NULL,
    reclamante_id INT NULL,
    titulo_processo NVARCHAR(10) NOT NULL UNIQUE,
    status_processo NVARCHAR(50) NULL,
    path_processo NVARCHAR(200) NOT NULL UNIQUE,
    ano SMALLINT NOT NULL,
    data_audiencia DATETIME NULL,
    created_at DATETIME DEFAULT GETDATE(),

    FOREIGN KEY (reclamante_id) REFERENCES Reclamantes(reclamante_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (motivo_id) REFERENCES Motivos(motivo_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
);

CREATE TABLE RelacaoProcessoReclamado(
    processo_id INT NOT NULL,
    reclamado_id INT NULL,
    created_at DATETIME DEFAULT GETDATE(),

    FOREIGN KEY (processo_id) REFERENCES ProcessosAdministrativos(processo_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (reclamado_id) REFERENCES Reclamados(reclamado_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
);

CREATE TABLE HistoricoMudancaStatus(
    processo_id INT,
    status_old NVARCHAR(50) NULL,
    status_new NVARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT GETDATE(),

    FOREIGN KEY (processo_id) REFERENCES ProcessosAdministrativos(processo_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
);
