# Backend: Gestão de Identidades (RF-001)

Módulo responsável pela API de Autenticação e Cadastro de Pessoas. Construído com FastAPI e seguindo o padrão arquitetural MVC+S (Models, Views/Routers, Controllers/Services) para interagir com o PostgreSQL (Supabase).

## Configuração Inicial

1. **Variáveis de Ambiente:** Crie um arquivo `.env` na raiz desta pasta `backend/` seguindo o modelo:
   ```env
   SUPABASE_URL=[https://seu-projeto.supabase.co](https://seu-projeto.supabase.co)
   SUPABASE_KEY=sua_chave_aqui
   PORT=8000

```

2. **Ambiente Virtual (Linux/Mac):**
```bash
python3 -m venv venv
source venv/bin/activate

```


*(No Windows, utilize `venv\Scripts\activate`)*
3. **Instalação das Dependências:**
Com o `venv` ativado, instale as bibliotecas necessárias:
```bash
pip install fastapi uvicorn httpx pydantic "pydantic[email]" python-dotenv bcrypt

```



## Como Executar Localmente

Para iniciar o servidor de desenvolvimento, rode:

```bash
uvicorn main:app --reload --port 8000

```

## Documentação da API

A documentação interativa (Swagger) é gerada automaticamente pelo FastAPI. Com o servidor rodando, acesse:

* **Swagger UI:** http://localhost:8000/docs

O contrato estático oficial também está disponível na raiz do projeto em `../../../docs/api/swagger.json`.

