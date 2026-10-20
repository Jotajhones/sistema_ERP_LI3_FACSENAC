# Backend: Tracking de Clientes e Contatos via WhatsApp (RF-007)

API REST desenvolvida em **FastAPI (Python)** e integrada ao PostgreSQL/Supabase, responsável pelo gerenciamento e registro do fluxo de contato com clientes que possuem orçamentos pendentes via protocolo `wa.me` (WhatsApp Web).

---

## O Motivo deste Módulo

O RF-007 resolve o gap de fechamento de negócios no ERP. Vendedores agora podem monitorar orçamentos em aberto, filtrar clientes que ainda não foram abordados, acionar a conversa no WhatsApp Web com mensagem pré-formatada e registrar o evento de contato de forma auditável e segura, mitigando fraudes e atribuindo a autoria estritamente pelo token de autenticação.

---

## Como Executar Localmente

A arquitetura do ERP utiliza o carregador dinâmico central (`importlib`) para compor os microsserviços. Por isso, a execução é feita a partir da pasta raiz do RF-001:

1. Navegue até a pasta do motor base:
```bash
cd src/rf-001-gestao-identidade/backend
```

2. Certifique-se de que o ambiente virtual está ativo e o `.env` configurado.

3. Inicie o servidor de desenvolvimento:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## Endpoints Disponíveis

* **`GET /orcamentos/pendentes-contato`**
  * **Descrição:** Retorna a listagem de orçamentos com status `PENDENTE` que ainda não foram contatados por nenhum vendedor, incluindo o número de telefone sanitizado do cliente.
  * **Permissão Obrigatória:** Usuário autenticado (`Bearer Token`).

* **`POST /orcamentos/{id}/contato` (ou `/orcamentos/{id}/contatar`)**
  * **Descrição:** Registra que o cliente do orçamento foi abordado via WhatsApp.
  * **Validação Anti-IDOR / RN-01:** Rejeita requisições para orçamentos inexistentes (`HTTP 404`) ou que já tenham sido convertidos em vendas (`HTTP 409 Conflict`).
  * **Atribuição Segura / RN-05:** O `vendedor_id` é inferido diretamente da credencial Bearer assinada, impossibilitando falsificação no payload.
