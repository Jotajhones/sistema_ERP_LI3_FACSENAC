CREATE TABLE produtos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(150) NOT NULL,
    descricao TEXT,
    valor_venda NUMERIC(10,2) NOT NULL,
    sku VARCHAR(100) NOT NULL UNIQUE,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    criado_por UUID,
    atualizado_por UUID,
    deletado_por UUID,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_produtos_valor_venda
        CHECK (valor_venda >= 0),
    CONSTRAINT fk_produtos_criado_por
        FOREIGN KEY (criado_por)
        REFERENCES users(id),
    CONSTRAINT fk_produtos_atualizado_por
        FOREIGN KEY (atualizado_por)
        REFERENCES users(id),
    CONSTRAINT fk_produtos_deletado_por
        FOREIGN KEY (deletado_por)
        REFERENCES users(id)
);

CREATE TABLE sessoes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    token_uuid UUID NOT NULL UNIQUE,
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sessoes_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

ALTER TABLE pessoas
ADD COLUMN ativo BOOLEAN NOT NULL DEFAULT TRUE;

ALTER TABLE users
ADD COLUMN ativo BOOLEAN NOT NULL DEFAULT TRUE;
