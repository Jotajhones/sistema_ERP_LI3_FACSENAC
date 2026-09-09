# Backend: Módulo de Catálogo e Sessões Restritas (RF-002)

API REST desenvolvida em **FastAPI (Python)** e integrada ao PostgreSQL/Supabase, responsável pela gestão segura do catálogo de produtos e validação de permissões no servidor.

## Configuração Inicial

1. Certifique-se de configurar as variáveis de ambiente necessárias em um arquivo `.env` (como a URL de conexão com o Supabase).
2. Instancie o ambiente virtual e instale as dependências:
```bash
pip install -r requirements.txt

```

## Como Executar Localmente

Execute o servidor de desenvolvimento utilizando o Uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000

```

## Arquitetura e Endpoints Principais

* **Autenticação e Sessões:** Validação de tokens opacos (UUIDv4) consultando a tabela `sessoes` no banco de dados.
* **Rotas Protegidas:** O endpoint `/produtos` exige o cabeçalho `Authorization: Bearer <token>`.
* **RBAC no Back-end:** Funções de dependência (`exigir_role`) barram requisições de perfis não autorizados (como Vendedores tentando executar operações de escrita), retornando erro `403 Forbidden`.
* **Segurança (A03):** Consultas ao PostgREST tratadas com `build_safe_query` para mitigação de injeções via query string.