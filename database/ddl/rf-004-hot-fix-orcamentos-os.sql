-- 1. GESTÃO DE ENDEREÇOS
CREATE TABLE IF NOT EXISTS enderecos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pessoa_id UUID NOT NULL,
    cep VARCHAR(9),
    logradouro VARCHAR(255),
    numero VARCHAR(20),
    complemento VARCHAR(100),
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    estado VARCHAR(2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_enderecos_pessoa 
        FOREIGN KEY (pessoa_id) 
        REFERENCES pessoas(id) 
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_enderecos_pessoa ON enderecos(pessoa_id);


-- 2. DUALIDADE PDV: ORÇAMENTOS (RASCUNHO / BALCÃO RÁPIDO)
CREATE TABLE IF NOT EXISTS orcamentos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cliente_id UUID NULL,
    nome_cliente VARCHAR(150),
    cpf_cliente VARCHAR(14),
    itens JSONB NOT NULL,
    valor_total NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDENTE',
    vendedor_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_orcamentos_vendedor 
        FOREIGN KEY (vendedor_id) 
        REFERENCES users(id) 
        ON DELETE SET NULL,
    CONSTRAINT chk_status_orcamento 
        CHECK (status IN ('PENDENTE', 'CONVERTIDO'))
);

CREATE INDEX IF NOT EXISTS idx_orcamentos_vendedor ON orcamentos(vendedor_id);


-- 3. DUALIDADE PDV: ORDENS DE SERVIÇO (VENDA REAL)
CREATE TABLE IF NOT EXISTS ordens_servico (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    orcamento_id UUID NULL,
    cliente_id UUID NULL, 
    vendedor_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ABERTA', 
    tipo_pagamento VARCHAR(50), 
    valor_total NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    desconto NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_os_cliente 
        FOREIGN KEY (cliente_id) 
        REFERENCES pessoas(id) 
        ON DELETE RESTRICT,
    CONSTRAINT fk_os_vendedor 
        FOREIGN KEY (vendedor_id) 
        REFERENCES users(id) 
        ON DELETE RESTRICT,
    CONSTRAINT fk_os_orcamento 
        FOREIGN KEY (orcamento_id) 
        REFERENCES orcamentos(id) 
        ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_os_cliente ON ordens_servico(cliente_id);
CREATE INDEX IF NOT EXISTS idx_os_status ON ordens_servico(status);


-- 4. TABELA ASSOCIATIVA DE ITENS DA OS (BAIXA DE ESTOQUE)
CREATE TABLE IF NOT EXISTS ordens_servico_itens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    os_id UUID NOT NULL,
    produto_id UUID NOT NULL,
    quantidade NUMERIC(12,3) NOT NULL,
    preco_unitario NUMERIC(10,2) NOT NULL,
    subtotal NUMERIC(10,2) NOT NULL,
    CONSTRAINT fk_os_itens_os 
        FOREIGN KEY (os_id) 
        REFERENCES ordens_servico(id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_os_itens_produto 
        FOREIGN KEY (produto_id) 
        REFERENCES produtos(id) 
        ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_os_itens_os ON ordens_servico_itens(os_id);


-- 5. MECANISMO DE AUTOLIMPEZA DE SESSÕES (SEGURANÇA)
CREATE OR REPLACE FUNCTION limpar_sessoes_expiradas()
RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM sessoes WHERE criado_em < NOW() - INTERVAL '23 hours';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_limpar_sessoes ON sessoes;
CREATE TRIGGER trigger_limpar_sessoes
BEFORE INSERT ON sessoes
FOR EACH STATEMENT
EXECUTE FUNCTION limpar_sessoes_expiradas();


-- 6. GATILHO DE BAIXA E ESTORNO DE ESTOQUE (PRODUTOS)
CREATE OR REPLACE FUNCTION atualizar_estoque_os()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE produtos 
        SET quantidade_estoque = quantidade_estoque - NEW.quantidade 
        WHERE id = NEW.produto_id;
        RETURN NEW;
        
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE produtos 
        SET quantidade_estoque = quantidade_estoque + OLD.quantidade 
        WHERE id = OLD.produto_id;
        RETURN OLD;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_atualizar_estoque ON ordens_servico_itens;
CREATE TRIGGER trigger_atualizar_estoque
AFTER INSERT OR DELETE ON ordens_servico_itens
FOR EACH ROW
EXECUTE FUNCTION atualizar_estoque_os();