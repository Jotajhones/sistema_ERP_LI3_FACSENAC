ALTER TABLE produtos
ADD COLUMN quantidade_estoque NUMERIC(12,3) NOT NULL DEFAULT 0;

ALTER TABLE produtos
ADD COLUMN unidade_medida VARCHAR(20) NOT NULL DEFAULT 'UN';

ALTER TABLE produtos
ADD CONSTRAINT chk_estoque_positivo
CHECK (quantidade_estoque >= 0);

ALTER TABLE produtos 
ADD COLUMN busca_textual tsvector 
GENERATED ALWAYS AS (
    to_tsvector('portuguese', coalesce(nome, '') || ' ' || coalesce(descricao, ''))
) STORED;

CREATE INDEX idx_produtos_busca_gin ON produtos USING GIN (busca_textual);