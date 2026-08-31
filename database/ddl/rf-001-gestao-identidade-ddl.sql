CREATE TYPE user_role AS ENUM (
    'ADMIN',
    'GESTOR',
    'VENDEDOR',
    'CLIENTE'
);

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(60) NOT NULL,
    user_role user_role NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE pessoas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE,
    nome VARCHAR(150) NOT NULL,
    cpf VARCHAR(11) NOT NULL UNIQUE,
    CONSTRAINT fk_pessoas_users
        FOREIGN KEY (user_id)
        REFERENCES users(id)
);