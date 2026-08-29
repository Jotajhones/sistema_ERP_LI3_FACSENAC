INSERT INTO users (id, email, password_hash, user_role)
VALUES
    ('UUID-ADMIN', 'admin@erp.com', '$2b$12$HASH_REAL', 'ADMIN'),
    ('UUID-GESTOR', 'gestor@erp.com', '$2b$12$HASH_REAL', 'GESTOR'),
    ('UUID-VENDEDOR', 'vendedor@erp.com', '$2b$12$HASH_REAL', 'VENDEDOR'),
    ('UUID-CLIENTE', 'cliente@erp.com', '$2b$12$HASH_REAL', 'CLIENTE');

INSERT INTO pessoas (id, user_id, nome, cpf)
VALUES
    ('UUID-PESSOA-ADMIN', 'UUID-ADMIN', 'Administrador Teste', '11111111111'),
    ('UUID-PESSOA-GESTOR', 'UUID-GESTOR', 'Gestor Teste', '22222222222'),
    ('UUID-PESSOA-VENDEDOR', 'UUID-VENDEDOR', 'Vendedor Teste', '33333333333'),
    ('UUID-PESSOA-CLIENTE', 'UUID-CLIENTE', 'Cliente Teste', '44444444444');