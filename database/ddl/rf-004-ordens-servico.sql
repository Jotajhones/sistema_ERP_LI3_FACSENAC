-- ====================================================================
-- RF-004 / SPRINT 4: ESTRUTURA DE ORDENS DE SERVIÇO E BAIXA DE ESTOQUE
-- ====================================================================

-- 1. Criação do tipo enumerado para controle de status da Ordem de Serviço
DO $$ 
BEGIN
    CREATE TYPE status_ordem_servico AS ENUM ('ABERTA', 'EM_ANDAMENTO', 'FECHADA', 'CANCELADA');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

-- 2. Tabela principal de Ordens de Serviço (ordens_servico)
CREATE TABLE IF NOT EXISTS ordens_servico (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    numero_os SERIAL UNIQUE,
    cliente_id UUID NOT NULL,
    vendedor_id UUID NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'ABERTA',
    valor_total NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    observacoes TEXT,
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_os_cliente
        FOREIGN KEY (cliente_id)
        REFERENCES pessoas(id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_os_vendedor
        FOREIGN KEY (vendedor_id)
        REFERENCES users(id)
        ON DELETE RESTRICT,
    CONSTRAINT chk_os_status
        CHECK (UPPER(status) IN ('ABERTA', 'EM_ANDAMENTO', 'FECHADA', 'CANCELADA')),
    CONSTRAINT chk_os_valor_total_positivo
        CHECK (valor_total >= 0)
);

-- Índices operacionais para performance de buscas e filtros
CREATE INDEX IF NOT EXISTS idx_os_cliente_id ON ordens_servico(cliente_id);
CREATE INDEX IF NOT EXISTS idx_os_vendedor_id ON ordens_servico(vendedor_id);
CREATE INDEX IF NOT EXISTS idx_os_status ON ordens_servico(status);
CREATE INDEX IF NOT EXISTS idx_os_criado_em ON ordens_servico(criado_em DESC);

-- 3. Tabela associativa de itens da Ordem de Serviço (os_produtos)
CREATE TABLE IF NOT EXISTS os_produtos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ordem_servico_id UUID NOT NULL,
    produto_id UUID NOT NULL,
    quantidade NUMERIC(12,3) NOT NULL,
    valor_unitario NUMERIC(10,2) NOT NULL,
    subtotal NUMERIC(12,2) GENERATED ALWAYS AS (quantidade * valor_unitario) STORED,
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_os_produtos_ordem
        FOREIGN KEY (ordem_servico_id)
        REFERENCES ordens_servico(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_os_produtos_produto
        FOREIGN KEY (produto_id)
        REFERENCES produtos(id)
        ON DELETE RESTRICT,
    CONSTRAINT chk_os_produtos_quantidade_positiva
        CHECK (quantidade > 0),
    CONSTRAINT chk_os_produtos_valor_unitario_positivo
        CHECK (valor_unitario >= 0),
    CONSTRAINT uq_os_produto_item
        UNIQUE (ordem_servico_id, produto_id)
);

CREATE INDEX IF NOT EXISTS idx_os_produtos_ordem_id ON os_produtos(ordem_servico_id);
CREATE INDEX IF NOT EXISTS idx_os_produtos_produto_id ON os_produtos(produto_id);

-- 4. Função e Gatilho (Trigger) para débito automático de estoque ao converter OS para 'Fechada'
CREATE OR REPLACE FUNCTION debitar_estoque_fechamento_os()
RETURNS TRIGGER AS $$
DECLARE
    registro_item RECORD;
    saldo_atual NUMERIC(12,3);
BEGIN
    -- Dispara apenas quando o status transiciona para 'FECHADA' (case-insensitive)
    IF (UPPER(NEW.status) = 'FECHADA' AND (OLD.status IS NULL OR UPPER(OLD.status) <> 'FECHADA')) THEN
        FOR registro_item IN
            SELECT produto_id, quantidade
            FROM os_produtos
            WHERE ordem_servico_id = NEW.id
        LOOP
            -- Bloqueio da linha para concorrência segura
            SELECT quantidade_estoque INTO saldo_atual
            FROM produtos
            WHERE id = registro_item.produto_id
            FOR UPDATE;

            IF saldo_atual IS NULL THEN
                RAISE EXCEPTION 'Produto % inexistente no catálogo para baixa de estoque.', registro_item.produto_id;
            END IF;

            IF saldo_atual < registro_item.quantidade THEN
                RAISE EXCEPTION 'Estoque insuficiente para o produto %. Saldo disponível: %, Quantidade exigida na OS: %.',
                    registro_item.produto_id, saldo_atual, registro_item.quantidade;
            END IF;

            -- Execução do débito de estoque
            UPDATE produtos
            SET quantidade_estoque = quantidade_estoque - registro_item.quantidade,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = registro_item.produto_id;
        END LOOP;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_baixa_estoque_fechamento_os ON ordens_servico;

CREATE TRIGGER trg_baixa_estoque_fechamento_os
AFTER UPDATE OF status ON ordens_servico
FOR EACH ROW
EXECUTE FUNCTION debitar_estoque_fechamento_os();

-- 5. Função e Gatilho auxiliar para atualização de timestamp na OS
CREATE OR REPLACE FUNCTION atualizar_timestamp_ordem_servico()
RETURNS TRIGGER AS $$
BEGIN
    NEW.atualizado_em = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_atualizar_timestamp_os ON ordens_servico;

CREATE TRIGGER trg_atualizar_timestamp_os
BEFORE UPDATE ON ordens_servico
FOR EACH ROW
EXECUTE FUNCTION atualizar_timestamp_ordem_servico();
