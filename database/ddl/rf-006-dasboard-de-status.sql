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
        SELECT o.status, o.valor_total
        FROM public.orcamentos o
        WHERE (p_data_inicio IS NULL
               OR o.created_at >= (p_data_inicio::timestamp AT TIME ZONE 'America/Sao_Paulo'))
          AND (p_data_fim IS NULL
               OR o.created_at <  ((p_data_fim + 1)::timestamp AT TIME ZONE 'America/Sao_Paulo'))
    )

    SELECT json_build_object(
        'periodo', json_build_object(
            'data_inicio', p_data_inicio,
            'data_fim',    p_data_fim
        ),
        'total_orcamentos', count(*),
        'convertidos',      count(*) FILTER (WHERE status = 'CONVERTIDO'),
        'pendentes',        count(*) FILTER (WHERE status = 'PENDENTE'),
        'taxa_conversao',   COALESCE(
                                round(100.0 * count(*) FILTER (WHERE status = 'CONVERTIDO')
                                      / NULLIF(count(*), 0), 2),
                                0),
        'valor_total_orcado',
            COALESCE(sum(valor_total), 0),
        'valor_total_convertido',
            COALESCE(sum(valor_total) FILTER (WHERE status = 'CONVERTIDO'), 0)
    )
    FROM base;
$$;

COMMENT ON FUNCTION public.rf006_conversao_orcamentos(date, date) IS
    'RF-006: taxa de conversão de orçamentos em vendas, por período (fuso America/Sao_Paulo). Uso exclusivo do backend (service_role).';

REVOKE ALL ON FUNCTION public.rf006_conversao_orcamentos(date, date)
    FROM PUBLIC, anon, authenticated;

GRANT EXECUTE ON FUNCTION public.rf006_conversao_orcamentos(date, date)
    TO service_role;

NOTIFY pgrst, 'reload schema';