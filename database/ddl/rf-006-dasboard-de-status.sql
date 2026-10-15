CREATE INDEX IF NOT EXISTS idx_orcamentos_periodo_status
    ON public.orcamentos (created_at)
    INCLUDE (status, valor_total);

CREATE OR REPLACE FUNCTION public.rf006_conversao_orcamentos(
    p_data_inicio date DEFAULT NULL,
    p_data_fim    date DEFAULT NULL
)

RETURNS json
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
    WITH base AS (
        SELECT 

            CASE 
                WHEN os.id IS NOT NULL THEN 'CONVERTIDO'
                ELSE o.status
            END as status_real,
            o.valor_total
        FROM public.orcamentos o
        LEFT JOIN public.ordens_servico os ON os.orcamento_id = o.id
        WHERE (p_data_inicio IS NULL OR o.created_at >= (p_data_inicio::timestamp AT TIME ZONE 'America/Sao_Paulo'))
          AND (p_data_fim IS NULL OR o.created_at < ((p_data_fim + 1)::timestamp AT TIME ZONE 'America/Sao_Paulo'))
    )
    SELECT json_build_object(
        'periodo', json_build_object(
            'data_inicio', p_data_inicio,
            'data_fim',    p_data_fim
        ),
        'total_orcamentos', count(*),
        
        -- Mandando as chaves em dobro para driblar a tipagem do Python e do JS
        'convertidos', count(*) FILTER (WHERE status_real IN ('CONVERTIDO', 'FINALIZADA', 'FINALIZADO')),
        'orcamentos_convertidos', count(*) FILTER (WHERE status_real IN ('CONVERTIDO', 'FINALIZADA', 'FINALIZADO')),
        
        'pendentes', count(*) FILTER (WHERE status_real NOT IN ('CONVERTIDO', 'FINALIZADA', 'FINALIZADO')),
        'orcamentos_pendentes', count(*) FILTER (WHERE status_real NOT IN ('CONVERTIDO', 'FINALIZADA', 'FINALIZADO')),
        
        'taxa_conversao', COALESCE(
                            round(100.0 * count(*) FILTER (WHERE status_real IN ('CONVERTIDO', 'FINALIZADA', 'FINALIZADO'))
                                  / NULLIF(count(*), 0), 2),
                            0),
        
        'valor_total_orcado', COALESCE(sum(valor_total), 0),
        'valor_total_convertido', COALESCE(sum(valor_total) FILTER (WHERE status_real IN ('CONVERTIDO', 'FINALIZADA', 'FINALIZADO')), 0)
    )
    FROM base;
$$;

-- Mantendo as permissões abertas para o Python acessar sem erro 500
GRANT EXECUTE ON FUNCTION public.rf006_conversao_orcamentos(date, date) TO anon, authenticated, service_role;
NOTIFY pgrst, 'reload schema';