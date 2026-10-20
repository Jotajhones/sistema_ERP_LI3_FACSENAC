UPDATE pessoas 
SET telefone = '5561911111111' 
WHERE user_id = '11111111-1111-1111-1111-111111111111';

UPDATE pessoas 
SET telefone = '5561922222222' 
WHERE user_id = '22222222-2222-2222-2222-222222222222';

UPDATE pessoas 
SET telefone = '5561933333333' 
WHERE user_id = '33333333-3333-3333-3333-333333333333';

UPDATE pessoas 
SET telefone = '5561999998888' 
WHERE user_id = '44444444-4444-4444-4444-444444444444';

INSERT INTO orcamentos (nome_cliente, cpf_cliente, telefone_cliente, itens, valor_total, status, vendedor_id)
VALUES (
    'Cliente Exemplo Zap',
    '12345678901',
    '5561999998888',
    '[{"produto_id": "00000000-0000-0000-0000-000000000000", "nome": "Produto Exemplo", "quantidade": 2, "preco_unitario": 50.00}]'::jsonb,
    100.00,
    'PENDENTE',
    '11111111-1111-1111-1111-111111111111'
);
