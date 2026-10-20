-- =========================================================================
-- RF-007: Tracking de Clientes e Contatos via WhatsApp
-- =========================================================================

-- 1. Colunas de telefone nas entidades base
ALTER TABLE public.pessoas ADD COLUMN IF NOT EXISTS telefone VARCHAR(20);
ALTER TABLE public.orcamentos ADD COLUMN IF NOT EXISTS telefone_cliente VARCHAR(20);

-- 2. Tabela relacional de auditoria de contatos de orçamentos (Card 51)
CREATE TABLE IF NOT EXISTS public.orcamentos_contatos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    orcamento_id UUID NOT NULL UNIQUE,
    vendedor_id UUID NOT NULL,
    contatado BOOLEAN NOT NULL DEFAULT TRUE,
    data_contato TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_contato_orcamento 
        FOREIGN KEY (orcamento_id) 
        REFERENCES public.orcamentos(id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_contato_vendedor 
        FOREIGN KEY (vendedor_id) 
        REFERENCES public.users(id)
);

-- 3. Índices de performance para busca relacional
CREATE INDEX IF NOT EXISTS idx_contatos_orcamento ON public.orcamentos_contatos(orcamento_id);
CREATE INDEX IF NOT EXISTS idx_contatos_vendedor ON public.orcamentos_contatos(vendedor_id);

-- 4. Permissões de acesso
GRANT ALL ON public.orcamentos_contatos TO anon, authenticated, service_role;
NOTIFY pgrst, 'reload schema';