-- =========================================================================
-- SPRINT 7: Auditoria, Logs e Recuperação de Acesso
-- =========================================================================

-- 1. TABELA DE TOKENS DE RECUPERAÇÃO DE SENHA (USO ÚNICO E EXPIRAÇÃO)
CREATE TABLE IF NOT EXISTS public.recuperacao_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    token_jti VARCHAR(100) NOT NULL UNIQUE,
    token_hash VARCHAR(255) NOT NULL,
    usado BOOLEAN NOT NULL DEFAULT FALSE,
    expira_em TIMESTAMP WITH TIME ZONE NOT NULL,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_recuperacao_usuario
        FOREIGN KEY (user_id)
        REFERENCES public.users(id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_recuperacao_jti ON public.recuperacao_tokens(token_jti);
CREATE INDEX IF NOT EXISTS idx_recuperacao_user ON public.recuperacao_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_recuperacao_expira ON public.recuperacao_tokens(expira_em);

-- 2. TABELA ESPELHO DE AUDITORIA DE PRODUTOS
CREATE TABLE IF NOT EXISTS public.audit_produtos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    produto_id UUID,
    acao VARCHAR(10) NOT NULL, -- 'INSERT', 'UPDATE', 'DELETE'
    dados_anteriores JSONB,
    dados_novos JSONB,
    usuario_id UUID,
    data_hora TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_produtos_data ON public.audit_produtos(data_hora DESC);
CREATE INDEX IF NOT EXISTS idx_audit_produtos_id ON public.audit_produtos(produto_id);

-- 3. TRIGGER AUTOMÁTICA DE AUDITORIA EM PRODUTOS
CREATE OR REPLACE FUNCTION public.fn_audit_produtos()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT') THEN
        INSERT INTO public.audit_produtos (produto_id, acao, dados_anteriores, dados_novos, data_hora)
        VALUES (NEW.id, 'INSERT', NULL, to_jsonb(NEW), CURRENT_TIMESTAMP);
        RETURN NEW;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO public.audit_produtos (produto_id, acao, dados_anteriores, dados_novos, data_hora)
        VALUES (NEW.id, 'UPDATE', to_jsonb(OLD), to_jsonb(NEW), CURRENT_TIMESTAMP);
        RETURN NEW;
    ELSIF (TG_OP = 'DELETE') THEN
        INSERT INTO public.audit_produtos (produto_id, acao, dados_anteriores, dados_novos, data_hora)
        VALUES (OLD.id, 'DELETE', to_jsonb(OLD), NULL, CURRENT_TIMESTAMP);
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_audit_produtos ON public.produtos;
CREATE TRIGGER trg_audit_produtos
AFTER INSERT OR UPDATE OR DELETE ON public.produtos
FOR EACH ROW EXECUTE FUNCTION public.fn_audit_produtos();

-- 4. TABELA ESPELHO DE AUDITORIA DE ORDENS DE SERVIÇO (OS)
CREATE TABLE IF NOT EXISTS public.audit_os (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    os_id UUID,
    acao VARCHAR(10) NOT NULL, -- 'INSERT', 'UPDATE', 'DELETE'
    dados_anteriores JSONB,
    dados_novos JSONB,
    usuario_id UUID,
    data_hora TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_os_data ON public.audit_os(data_hora DESC);
CREATE INDEX IF NOT EXISTS idx_audit_os_id ON public.audit_os(os_id);

-- 5. TRIGGER AUTOMÁTICA DE AUDITORIA EM ORDENS DE SERVIÇO
CREATE OR REPLACE FUNCTION public.fn_audit_os()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT') THEN
        INSERT INTO public.audit_os (os_id, acao, dados_anteriores, dados_novos, data_hora)
        VALUES (NEW.id, 'INSERT', NULL, to_jsonb(NEW), CURRENT_TIMESTAMP);
        RETURN NEW;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO public.audit_os (os_id, acao, dados_anteriores, dados_novos, data_hora)
        VALUES (NEW.id, 'UPDATE', to_jsonb(OLD), to_jsonb(NEW), CURRENT_TIMESTAMP);
        RETURN NEW;
    ELSIF (TG_OP = 'DELETE') THEN
        INSERT INTO public.audit_os (os_id, acao, dados_anteriores, dados_novos, data_hora)
        VALUES (OLD.id, 'DELETE', to_jsonb(OLD), NULL, CURRENT_TIMESTAMP);
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_audit_os ON public.ordens_servico;
CREATE TRIGGER trg_audit_os
AFTER INSERT OR UPDATE OR DELETE ON public.ordens_servico
FOR EACH ROW EXECUTE FUNCTION public.fn_audit_os();

-- 6. PERMISSÕES DE ACESSO
GRANT ALL ON public.recuperacao_tokens TO anon, authenticated, service_role;
GRANT ALL ON public.audit_produtos TO anon, authenticated, service_role;
GRANT ALL ON public.audit_os TO anon, authenticated, service_role;

NOTIFY pgrst, 'reload schema';
