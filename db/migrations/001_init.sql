CREATE TABLE IF NOT EXISTS TITULOS_PUBLICOS (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        expressao TEXT,
        data_vencimento TEXT NOT NULL,  -- formato ISO: YYYY-MM-DD
        tipo_titulo TEXT NOT NULL,
        data_base TEXT,
        codigo_selic TEXT,
        codigo_isin TEXT,
        status TEXT NOT NULL DEFAULT 'ATIVO'
               CHECK (status IN ('ATIVO','INATIVO','SUSPENSO','CANCELADO','RESGATADO')),
        UNIQUE(tipo_titulo, data_vencimento)  -- garante unicidade do conjunto
    );

CREATE TABLE IF NOT EXISTS MERCADO_SECUNDARIO (
        titulo_id        INTEGER NOT NULL,              -- FK para TITULOS_PUBLICOS(id)
        data_referencia  TEXT    NOT NULL,              -- ISO YYYY-MM-DD
        taxa_anbima      REAL,
        intervalo_min_d0 REAL,
        intervalo_max_d0 REAL,
        intervalo_min_d1 REAL,
        intervalo_max_d1 REAL,
        pu               REAL,
        PRIMARY KEY (titulo_id, data_referencia),
        FOREIGN KEY (titulo_id) REFERENCES TITULOS_PUBLICOS(id)
    ) WITHOUT ROWID;