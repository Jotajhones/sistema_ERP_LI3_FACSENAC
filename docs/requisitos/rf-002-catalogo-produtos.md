### RF-002: Catálogo de Produtos e Gestão de Sessões

---

## 1. IDENTIFICAÇÃO DO REQUISITO 

**ID:** RF-002
**Título:** Catálogo de Produtos e Sessões Restritas
**Tipo:** Requisito Funcional
**Prioridade:** ALTA (Habilita a futura criação de Ordens de Serviço e Orçamentos)
**Complexidade:** ALTA (estimado 8 story points)
**Status:** EM DESENVOLVIMENTO
**Data de Criação:** 02/09/2026
**Última Atualização:** 02/09/2026

**Breve Descrição:**
Criar o catálogo de produtos do ERP com operações de CRUD e deleção lógica, protegido por um sistema de Sessões Opacas (UUID). O frontend apresentará um Dashboard inicial com controle de acesso baseado em papéis (RBAC), limitando ações administrativas para usuários comuns.

---

## 2. DESCRIÇÃO E ATORES 

**Contexto do negócio:**
Para que a loja possa operar e gerar orçamentos, os vendedores precisam visualizar os itens disponíveis no estoque. Simultaneamente, gestores precisam de uma interface para cadastrar e precificar novos materiais. Todo esse fluxo deve ocorrer em um ambiente seguro, onde apenas usuários autenticados têm acesso aos dados, e onde cada ação no catálogo deixa um rastro de auditoria.

**Atores do Sistema:**

### 1. Administrador e Gestor - Atores Principais

* **Papel:** Gerenciar o catálogo de produtos da loja.
* **Permissões:**
* CREATE (Cadastrar novos produtos).
* READ (Visualizar lista de produtos).
* UPDATE (Editar dados e preços).
* DELETE (Deleção lógica, inativando o produto).



### 2. Vendedor - Ator Secundário

* **Papel:** Consultar o catálogo para informar clientes e preparar futuras ordens de serviço.
* **Permissões:**
* READ (Visualizar produtos).
* *Não possui permissão de criação, edição ou exclusão de produtos.*



### 3. Sistema - Ator Secundário

* **Papel:** Interceptar requisições, validar tokens de sessão opaca, gerenciar a deleção em cascata e carimbar logs de auditoria no banco de dados.
* **Permissões:**
* Todas as operações internas no banco de dados, incluindo manipulação das tabelas `sessoes` e `produtos`.

---

## 3. ESPECIFICAÇÃO DE CASOS DE USO E REQUISITOS NÃO-FUNCIONAIS (20%)

**Caso de Uso (UC-002): Acessar Dashboard e Gerenciar Catálogo**

### Pré-Condições

* O usuário deve ter realizado login com sucesso (RF-001) e possuir um Token UUID válido armazenado no LocalStorage.
* A API deve estar em execução e conectada ao banco de dados PostgreSQL/Supabase.

### Pós-Condições (Sucesso)

* Os produtos ativos são exibidos na tela conforme as permissões do usuário (RBAC).
* Ações de criação/edição carimbam o ID do usuário nas colunas de auditoria do banco (`criado_por`, `atualizado_por`).

### Pós-Condições (Falha)

* Acesso negado com erro 401 (Unauthorized) caso o token seja inválido ou expirado.
* Redirecionamento forçado para a tela de login.

### Fluxo Principal

1. O usuário efetua login (RF-001) e o frontend armazena o token UUID e a `user_role` no LocalStorage.
2. O usuário é redirecionado para a tela de Dashboard (`/produtos.html`).
3. O Frontend executa um script Vanilla JS que avalia a `user_role` (RBAC Client-side).
4. Se a role for "VENDEDOR", o botão "Cadastrar Produto" recebe `display: none`.
5. O Frontend dispara um `fetch()` GET para `/produtos`, enviando o cabeçalho `Authorization: Bearer <token>`.
6. O Backend (Middleware) intercepta a requisição e busca o token na tabela `sessoes`.
7. O Backend identifica o `user_id` dono do token, injeta na requisição e permite o acesso à rota.
8. O Backend consulta a tabela `produtos` filtrando por `ativo == true`.
9. O Frontend recebe o JSON e renderiza dinamicamente a tabela de produtos na tela.

### Fluxo Alternativo A1: Cadastro de Produto (Gestor)

* 4a.1. O Gestor visualiza e clica no botão "Cadastrar Produto".
* 4a.2. O Frontend exibe um modal de formulário.
* 4a.3. O Gestor preenche os campos (Nome, Descrição, Valor, SKU).
* 4a.4. O Frontend valida se o valor não é negativo e dispara um POST com o Bearer Token.
* 4a.5. O Backend valida o token, insere o produto no banco gravando o `user_id` em `criado_por` e retorna 201 Created.

### Fluxo Alternativo A2: Sessão Inválida ou Expirada

* 6a.1. O Backend não encontra o token na tabela `sessoes`.
* 6a.2. O Backend retorna HTTP 401 Unauthorized.
* 6a.3. O Frontend intercepta o erro 401, limpa o LocalStorage e redireciona o usuário para `index.html`.

### Regras de Negócio

| ID | Regra | Descrição |
| --- | --- | --- |
| **RN-04** | Integridade de Preço | Nenhum produto pode ser cadastrado com `valor_venda` negativo (Constraint CHECK no BD). |
| **RN-05** | SKU Único | O código de barras/SKU deve ser único no sistema para evitar duplicidade de estoque. |
| **RN-06** | Deleção Lógica | Produtos nunca recebem `DELETE` físico. A inativação ocorre marcando o campo `ativo = false`. |
| **RN-07** | Rastreabilidade Base | Toda inserção ou alteração na tabela de produtos deve registrar o `user_id` logado (Auditoria). |
| **RN-08** | Limpeza de Sessão | Se um usuário for apagado, sua sessão deve ser invalidada automaticamente (`ON DELETE CASCADE`). |

### Requisitos Não-Funcionais (RNF)

| ID | Atributo | Requisito | Métrica | Justificativa |
| --- | --- | --- | --- | --- |
| **RNF-04** | Segurança | Todas as rotas de negócio devem exigir `Bearer Token`. | Validação de Middleware. | Bloquear acessos anônimos à API. |
| **RNF-05** | Usabilidade | Elementos não permitidos devem ser ocultados na UI. | Inspeção visual (RBAC). | Evitar frustração do usuário com botões que retornam erro. |
| **RNF-06** | Manutenibilidade | Manter entrypoint único da API. | Estrutura de pastas. | Evitar fragmentação de microsserviços desnecessários. |

---

## 4. PROTÓTIPO FUNCIONAL

**Mockup - Tela 1: Dashboard Vendedor (Sem permissão de criar)**

```text
┌─────────────────────────────────────────────────────────────────┐
│  ☰ ERP Construção       Olá, Vendedor           [ Sair ]        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📦 Catálogo de Produtos                                        │
│                                                                 │
│  ID   | SKU      | NOME               | VALOR                   │
│  -------------------------------------------------------------  │
│  001  | 789100   | Cimento CP II 50kg | R$ 35,90                │
│  002  | 789101   | Tijolo Baiano 8f   | R$ 0,95                 │
│                                                                 │
│  (Ações administrativas ocultadas via RBAC)                     │
└─────────────────────────────────────────────────────────────────┘

```

**Mockup - Tela 2: Dashboard Gestor (Com botão de ação)**

```text
┌─────────────────────────────────────────────────────────────────┐
│  ☰ ERP Construção       Olá, Gestor             [ Sair ]        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📦 Catálogo de Produtos                     [ + NOVO PRODUTO ] │
│                                                                 │
│  ID   | SKU      | NOME               | VALOR         | AÇÕES   │
│  -------------------------------------------------------------  │
│  001  | 789100   | Cimento CP II 50kg | R$ 35,90      | [✏️][🗑️] │
│  002  | 789101   | Tijolo Baiano 8f   | R$ 0,95       | [✏️][🗑️] │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

```

**Mockup - Tela 3: Cadastro de Produto (Modal)**

```text
┌─────────────────────────────────────────────────────────────────┐
│  Cadastro de Novo Produto                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Nome: [ Areia Média (Saco 20kg)                   ]            │
│  SKU:  [ 789102                                    ]            │
│  Valor: [ 5.50                                     ] ✅         │
│                                                                 │
│  [ CANCELAR ]                              [ SALVAR PRODUTO ]   │
└─────────────────────────────────────────────────────────────────┘

```

---

## 5. ARQUITETURA E ADR

### Diagrama de Componentes

```text
[Frontend (Vanilla JS/RBAC)] ---> Authorization: Bearer <UUID> ---> [FastAPI (Middleware Guardião)] ---> [Supabase/PostgreSQL]
        |                                                                      |                               |
        └--- Oculta UI baseada em user_role                                    └--- Valida UUID em sessoes     └--- Produtos (Soft Delete)

```

### ADR-005: Sessões Opacas (UUID) para Autenticação

* **Contexto:** Necessidade de proteger as rotas da API sem sobrecarregar a equipe com implementações complexas de JWT ou lidar com chaves criptográficas no Frontend.


* **Decisão:** Utilizar Tokens Opacos baseados em UUIDv4 armazenados em uma tabela `sessoes`.
* **Consequências:** Implementação simplificada e segura no backend, permitindo invalidação imediata de sessão no banco de dados.

### ADR-006: Deleção Lógica (Soft Delete)

* **Contexto:** Sistemas ERP exigem alta rastreabilidade para auditoria financeira. A exclusão de um produto pode quebrar ordens de serviço passadas.
* **Decisão:** Adicionar um campo `ativo BOOLEAN DEFAULT TRUE`. Exclusões apenas atualizam este campo para falso e registram o `deletado_por`.
* **Consequências:** Integridade referencial mantida a longo prazo; as rotas de GET precisam aplicar filtros explícitos (`ativo == true`).

### ADR-007: RBAC Client-Side com Vanilla JS

* **Contexto:** Usuários com restrições (vendedores) não devem tentar executar ações administrativas.
* **Decisão:** Controlar a renderização da interface via JavaScript, verificando a `user_role` armazenada na autenticação.
* **Consequências:** UX mais limpa; no entanto, a segurança real depende estritamente do bloqueio da rota no backend, já que o frontend pode ser manipulado no navegador.

---

## 7. DOCUMENTAÇÃO API (SWAGGER/OPENAPI)

O contrato da API REST continua integrado à especificação OpenAPI 3.0 do sistema (Entrypoint unificado).

* **Documentação Dinâmica (Swagger UI):** Disponível na rota `/docs`.
* **Novos Endpoints:**
* `GET /produtos` (Protegido via Bearer Token)
* `POST /produtos` (Protegido via Bearer Token, requer esquema JSON com nome, sku, valor)
* `PUT /produtos/{id}` (Protegido via Bearer Token)
* `DELETE /produtos/{id}` (Soft delete, Protegido via Bearer Token)


* **Security Schema:** Adição do componente `bearerAuth` no Swagger indicando que o token UUID deve ser passado nos Headers.

---

