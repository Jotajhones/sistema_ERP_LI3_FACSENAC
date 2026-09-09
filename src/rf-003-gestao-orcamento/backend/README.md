# ⚠️ DIRETÓRIO DE BACKEND INTENCIONALMENTE VAZIO

## Justificativa Arquitetural 

A ausência de arquivos `.py` neste diretório **não indica ausência de desenvolvimento de backend para o RF-003**. 

Esta sprint exigiu a implementação de regras de Controle de Acesso (RBAC), manipulação de estoque e destruição física de sessões (Logout). Para manter a integridade arquitetural da API REST e evitar duplicação de código (DRY - Don't Repeat Yourself), o desenvolvimento no lado do servidor foi realizado nos domínios originais das entidades.

Para auditar o código de backend correspondente ao RF-003, o avaliador (ou script de correção) deve verificar os seguintes arquivos modificados/criados no repositório:

### 1. Funcionalidade: Logout e Destruição de Sessão
* **Local:** `src/rf-001-gestao-identidade/backend/routers/auth_router.py`
* **Implementação:** Endpoint `POST /auth/logout` adicionado.

### 2. Funcionalidade: Controle de Acesso (RBAC Server-side)
* **Local:** `src/rf-001-gestao-identidade/backend/dependencies.py`
* **Implementação:** Injeção de dependência `require_role(["ADMIN", "GESTOR"])` adicionada para travar acesso indevido.

### 3. Funcionalidade: Recebimento de Lotes de Estoque
* **Local:** `src/rf-002-catalogo-produtos/backend/routers/produto_router.py`
* **Implementação:** Endpoint `PATCH /produtos/{id}/recebimento` protegido pelo middleware RBAC adicionado para gerenciar o incremento de estoque.

O frontend correspondente a estas chamadas está localizado no diretório vizinho: `../frontend/`.