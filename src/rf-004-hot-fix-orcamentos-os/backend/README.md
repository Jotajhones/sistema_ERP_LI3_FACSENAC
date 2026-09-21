# Backend: Motor Transacional e Hot-Fix Orçamentos/OS (RF-004)

API REST desenvolvida em **FastAPI (Python)** e integrada ao PostgreSQL/Supabase, responsável por garantir a integridade transacional das vendas e assumir o controle total das regras de faturamento e estoque.

## O Motivo deste Hot-Fix
Esta pasta foi criada para resgatar e implementar a persistência de dados do módulo de orçamentos (RF-003), que operava apenas de forma visual. Este módulo resolve a exigência do faturamento: o cálculo matemático passa a ser 100% server-side, habilitando a baixa automática de estoque, o cadastro silencioso de clientes anônimos de balcão e a conversão rastreável de orçamentos em Ordens de Serviço (OS) definitivas.

## Como Executar Localmente

A arquitetura do ERP utiliza um carregador dinâmico central (`importlib`) para unir os microsserviços. Por isso, **a execução deve ser feita obrigatoriamente a partir da pasta raiz do RF-001**.

1. Navegue até a pasta do motor base:
```bash
cd ../../rf-001-gestao-identidade/backend

```

2. Certifique-se de que o ambiente virtual está ativo e as variáveis `.env` configuradas.
3. Execute o servidor de desenvolvimento utilizando o Uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000

```

## Arquitetura e Regras de Negócio Principais

* **Matemática Server-Side:** O backend ignora os totais enviados pelo frontend, recalculando a matemática (Preço x Quantidade) com base nos valores originais do catálogo para evitar fraudes via manipulação de payloads.
* **Transações em Lote (Bulk Insert):** A conversão de um Orçamento em OS grava a venda, gera os múltiplos itens associados e realiza o débito do estoque na tabela de produtos simultaneamente.
* **Bloqueio Transacional (Estoque Negativo):** A API intercepta e retorna erro `409 Conflict` abortando a geração da OS caso o produto não tenha `quantidade_estoque` suficiente.
* **Prevenção IDOR (OWASP A01):** A rota de atualização de cadastros (`PUT /pessoas`) intercepta o acesso baseado no perfil, bloqueando vendedores de alterarem dados de administradores ou gestores, restringindo a edição exclusivamente a Clientes de Balcão (`user_id` NULO).
