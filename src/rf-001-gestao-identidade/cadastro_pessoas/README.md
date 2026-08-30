# Módulo de Cadastro de Pessoas (RF-001) - Miguel Nunes

Módulo da API FastAPI responsável pelo endpoint de cadastro e consulta de Pessoas (entidade física de negócio), garantindo a relação 1:1 com a tabela `users`.

## Requisitos

- Python 3.10+
- `pip install -r requirements.txt`

## Configuração

Copie o arquivo `.env.example` para `.env` e preencha as credenciais do Supabase:

```bash
cp .env.example .env
```

## Execução Local

Executando diretamente este módulo:

```bash
uvicorn main:app --reload --port 8001
```

A documentação interativa estará acessível em:
- Swagger: `http://localhost:8001/docs`

## Integração com a API Principal

Para integrar as rotas deste módulo à aplicação principal (`main.py` de `rf-001-gestao-identidade`), basta incluir o router:

```python
from cadastro_pessoas.main import router as pessoas_router

app.include_router(pessoas_router)
```

## Endpoints

- `POST /pessoas`: Cadastra uma pessoa vinculada a um `user_id` existente (valida CPF e relação 1:1).
- `GET /pessoas`: Lista todas as pessoas cadastradas.
- `GET /pessoas/user/{user_id}`: Consulta a pessoa vinculada ao `user_id`.
- `GET /health`: Healthcheck do serviço.
