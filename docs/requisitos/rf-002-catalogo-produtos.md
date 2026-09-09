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

### Fluxo Alternativo A3: Tentativa de Acesso por Vendedor (RBAC Bypass)
* 4a.1. O usuário (Vendedor) força a exibição do botão via console do navegador ou tenta chamar o POST pelo Postman.
* 4a.2. O Backend intercepta a requisição via `exigir_role(["ADMIN", "GESTOR"])`.
* 4a.3. O Backend retorna HTTP 403 Forbidden.
* 4a.4. A operação é negada e a segurança do banco mantida.

### Regras de Negócio

| ID | Regra | Descrição |
| --- | --- | --- |
| **RN-04** | Integridade de Preço | Nenhum produto pode ser cadastrado com `valor_venda` negativo (Constraint CHECK no BD). |
| **RN-05** | SKU Único | O código de barras/SKU deve ser único no sistema para evitar duplicidade de estoque. |
| **RN-06** | Deleção Lógica | Produtos nunca recebem `DELETE` físico. A inativação ocorre marcando o campo `ativo = false`. |
| **RN-07** | Rastreabilidade Base | Toda inserção ou alteração na tabela de produtos deve registrar o `user_id` logado (Auditoria). |
| **RN-08** | Limpeza de Sessão | Se um usuário for apagado, sua sessão deve ser invalidada automaticamente (`ON DELETE CASCADE`). |
| **RN-09** | Restrição de Papel (RBAC) | Apenas usuários com `user_role` de GESTOR/ADMIN podem executar operações de mutação (POST/PUT/DELETE) no catálogo. |

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
* **Status:** ACEITO
* **Contexto:** Proteger as rotas da API de forma segura.
* **Decisão:** Utilizar Tokens Opacos baseados em UUIDv4 armazenados na tabela `sessoes`.
* **Alternativas:** JWT (mais complexo para invalidação imediata), Cookies (problemas com CORS).
* **Consequências:** Implementação simples e invalidação de sessão instantânea no banco.

### ADR-006: Deleção Lógica (Soft Delete)
* **Status:** ACEITO
* **Contexto:** Sistemas ERP exigem rastreabilidade e integridade referencial.
* **Decisão:** Adicionar campo `ativo BOOLEAN DEFAULT TRUE` e atualizar para `false` na exclusão.
* **Alternativas:** `DELETE CASCADE` físico (perigoso para histórico de vendas).
* **Consequências:** Integridade mantida. Rotas GET precisam aplicar filtros explícitos.

### ADR-007: RBAC Client-Side com Vanilla JS
* **Status:** ACEITO
* **Contexto:** Evitar que vendedores tentem executar ações administrativas na UI.
* **Decisão:** Controlar o display via JS lendo o `user_role` do LocalStorage.
* **Alternativas:** Renderização server-side.
* **Consequências:** UX mais limpa.

### ADR-008: Validação Mista (Front e Back)
* **Status:** ACEITO
* **Contexto:** Garantir integridade de preços e nomes.
* **Decisão:** Validar no Vanilla JS e travar no banco com `CHECK (valor_venda >= 0)`.
* **Alternativas:** Validar apenas no Frontend.
* **Consequências:** Segurança absoluta contra bypass.

### Tecnologias Escolhidas
| Camada | Tecnologia | Versão | Justificativa |
|--------|-----------|--------|---------------|
| Frontend | HTML5/CSS3/Vanilla JS | ES2015+ | Requisito do laboratório e leveza. |
| Backend | FastAPI (Python) | 0.100+ | Alta performance e documentação Swagger nativa. |
| Banco de Dados| Supabase (PostgreSQL)| 15+ | RLS nativo e persistência robusta. |

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

## 8. VALIDAÇÃO DE SEGURANÇA OWASP

### Controle escolhido: A03:2021 — Injection

**Por que A03 e não A01 (Broken Access Control)?**
A tarefa de segurança permite escolher entre A03 (Injection) e A01 (Broken Access Control/RBAC). Optamos por A03 porque:
1. É um controle *aplicável e demonstrável hoje*: o padrão de código que o motiva já existe em produção (ver "Vulnerabilidade" abaixo).
2. Uma implementação real de A01 exigiria RBAC de verdade — hoje o `POST /auth` do RF-001 devolve apenas `{ role }`, sem nenhum token/sessão (JWT ou equivalente). Fazer RBAC funcionar exigiria projetar e construir essa infraestrutura de autenticação do zero, o que está fora do escopo "alterar apenas o necessário" desta entrega. Isso está registrado como próximo passo na seção 5.

### 8.1 Vulnerabilidade

**Onde:** o projeto não executa SQL diretamente — não há `psycopg2` nem ORM em uso (apesar de `psycopg2-binary` ainda constar em `requirements.txt` do RF-001, como resíduo). Todo acesso ao banco é feito por chamadas HTTP à API REST do Supabase (PostgREST), onde cada filtro é expresso na *query string* da URL no formato `coluna=operador.valor` (ex.: `email=eq.fulano@exemplo.com`).

Antes desta correção, três funções de repositório montavam essa query string concatenando a entrada do usuário diretamente com f-string, sem qualquer codificação:

```python
# auth_repository.py (ANTES)
url = f"/rest/v1/users?email=eq.{email}&select=id,email,password_hash,user_role"

# pessoas_repository.py (ANTES)
url = f"/rest/v1/pessoas?cpf=eq.{cpf}&select=*"
```

**Impacto:** caracteres com significado especial em uma query string HTTP — `&`, `=`, `,`, `*`, `#` — presentes no valor de entrada deixam de ser tratados como parte do valor e passam a ser interpretados como novos parâmetros/operadores da consulta ao PostgREST. Isso é uma instância de A03:2021 (Injection): entrada não confiável altera a estrutura de um comando/consulta, e não apenas seu conteúdo.

Ponto importante: esse ataque **não depende de burlar a validação de formato do Pydantic**. O campo `email` do RF-001 é `EmailStr`, mas `&`, `=`, `*` e `%` são caracteres válidos na parte local de um endereço de e-mail pela RFC 5322 — ou seja, um payload como `vendedor@erp.com&select=*,password_hash` é um e-mail *sintaticamente válido* e chega intacto até o repositório.

**Prova de conceito (antes da correção), payload no campo e-mail do `POST /auth`:**

```
Entrada:  vendedor@erp.com&select=*,password_hash

URL enviada ao Supabase:
/rest/v1/users?email=eq.vendedor@erp.com&select=*,password_hash&select=id,email,password_hash,user_role

Parâmetros que o servidor interpreta:
{'email': ['eq.vendedor@erp.com'],
 'select': ['*,password_hash', 'id,email,password_hash,user_role']}
```

O parâmetro `email` continua correto (o `&` delimita o fim do valor), mas o atacante consegue **injetar um segundo `select`**, inteiramente sob seu controle — o que abre espaço para tentativas de sobrescrever quais colunas são retornadas (ex.: forçar a exposição de `password_hash`, ou, no catálogo de produtos, de `custo_unitario`), além de poder injetar outros parâmetros do PostgREST (`limit`, `order`, `or=(...)`) para poluir ou tentar contornar filtros da consulta original.

A mesma classe de risco se repetia em `pessoas_repository.py` (`get_user_by_id`, `get_pessoa_by_user_id`, `get_pessoa_by_cpf`) e afetaria igualmente qualquer rota nova de produtos que seguisse o mesmo padrão — por isso a rota `GET /produtos/busca?termo=`, que recebe texto livre do usuário, foi escolhida como o exemplo central desta entrega.

### 8.2 Implementação

A mitigação foi centralizada em uma função utilitária, `build_safe_query()` (`postgrest_utils.py`, duplicada nos dois back-ends por eles serem módulos independentes/implantáveis separadamente, no mesmo espírito de `config.py`/`database.py`):

```python
from urllib.parse import urlencode, quote

def build_safe_query(filters: dict) -> str:
    return urlencode(
        {str(chave): str(valor) for chave, valor in filters.items()},
        quote_via=quote,
        safe="",
    )
```

Ela aplica *percent-encoding* a cada valor antes de montar a query string. Isso equivale, para uma API REST baseada em query string, ao que uma consulta parametrizada (*prepared statement*) faz para SQL puro: separa estruturalmente "código" (chaves/operadores da consulta, escritos pelo desenvolvedor) de "dado" (entrada do usuário). Um `&` digitado pelo usuário vira `%26` na URL; o servidor só decodifica esse valor de volta para `&` **depois** de já ter isolado o parâmetro ao qual ele pertence — portanto, nunca é interpretado como um novo delimitador.

**Aplicada retroativamente** (RF-001):

```python
# auth_repository.py (DEPOIS)
query = build_safe_query({
    "email": f"eq.{email}",
    "select": "id,email,password_hash,user_role",
})
url = f"/rest/v1/users?{query}"
```

```python
# pessoas_repository.py (DEPOIS) — mesmo padrão em get_user_by_id,
# get_pessoa_by_user_id e get_pessoa_by_cpf
query = build_safe_query({"cpf": f"eq.{cpf}", "select": "*"})
url = f"/rest/v1/pessoas?{query}"
```

**Aplicada desde o início** (RF-002, `produtos_repository.py`), com destaque para a rota de busca:

```python
def search_produtos_by_nome(termo: str) -> List[Dict[str, Any]]:
    # Um '*' digitado pelo usuário não pode virar um coringa adicional do
    # operador ilike — só os dois adicionados pelo próprio código valem.
    termo_sem_coringa = termo.replace("*", "")

    query = build_safe_query({
        "select": PUBLIC_COLUMNS,      # nunca inclui custo_unitario
        "ativo": "eq.true",
        "nome": f"ilike.*{termo_sem_coringa}*",
    })
    url = f"/rest/v1/produtos?{query}"
    ...
```

Duas camadas de defesa, portanto: (1) *encoding* estrutural — impede que o valor escape do parâmetro `nome`; (2) remoção do caractere `*` da entrada do usuário — impede que ele amplie, por conta própria, o único operador com significado especial que a própria rota usa de propósito (o coringa do `ilike`), mesmo depois de decodificado no servidor.

### 8.3 Teste / Evidência

Os testes rodam com biblioteca padrão do Python apenas (`urllib.parse`), sem depender de `httpx`/`pydantic`/`fastapi` instalados nem de conexão real com o Supabase: eles importam a função `build_safe_query` **de verdade** (o mesmo módulo usado pelos repositórios em produção) e reproduzem a lógica exata de montagem de URL de cada função, comparando o padrão antigo com o corrigido.

* `src/rf-001-gestao-identidade/backend/tests/test_a03_injection.py`
* `src/rf-002/backend/tests/test_a03_injection.py`

**Execução real — RF-001** (`python3 tests/test_a03_injection.py`, a partir de `src/rf-001-gestao-identidade/backend/`):

```
==============================================================================
Teste de Segurança - OWASP A03:2021 Injection (RF-001)
==============================================================================
[PASSOU] test_email_antigo_e_vulneravel_a_injecao
[PASSOU] test_email_corrigido_contem_payload_malicioso
[PASSOU] test_cpf_antigo_e_vulneravel_a_injecao
[PASSOU] test_cpf_corrigido_contem_payload_malicioso
------------------------------------------------------------------------------
Exemplo comparativo (payload: 'vendedor@erp.com&select=*,password_hash'):
  URL antiga (vulnerável):
    /rest/v1/users?email=eq.vendedor@erp.com&select=*,password_hash&select=id,email,password_hash,user_role
    -> parâmetros interpretados: {'email': ['eq.vendedor@erp.com'], 'select': ['*,password_hash', 'id,email,password_hash,user_role']}
  URL nova (corrigida):
    /rest/v1/users?email=eq.vendedor%40erp.com%26select%3D%2A%2Cpassword_hash&select=id%2Cemail%2Cpassword_hash%2Cuser_role
    -> parâmetros interpretados: {'email': ['eq.vendedor@erp.com&select=*,password_hash'], 'select': ['id,email,password_hash,user_role']}
------------------------------------------------------------------------------
RESULTADO: todos os 4 testes passaram.
```

**Execução real — RF-002** (`python3 tests/test_a03_injection.py`, a partir de `src/rf-002/backend/`):

```
==============================================================================
Teste de Segurança - OWASP A03:2021 Injection (RF-002 / produtos)
==============================================================================
[PASSOU] test_versao_antiga_seria_vulneravel_a_injecao
[PASSOU] test_busca_produtos_corrigida_contem_payload_malicioso
[PASSOU] test_usuario_nao_amplia_o_coringa_ilike
------------------------------------------------------------------------------
Exemplo comparativo (termo de busca: 'Cimento&select=*,custo_unitario'):
  Se a rota usasse o padrão antigo (hipotético/vulnerável):
    /rest/v1/produtos?select=id,nome,descricao,categoria,preco_venda,estoque,ativo&ativo=eq.true&nome=ilike.*Cimento&select=*,custo_unitario*
    -> parâmetros interpretados: {'select': ['id,nome,descricao,categoria,preco_venda,estoque,ativo', '*,custo_unitario*'], 'ativo': ['eq.true'], 'nome': ['ilike.*Cimento']}
  Implementação real desta rota (corrigida):
    /rest/v1/produtos?select=id%2Cnome%2Cdescricao%2Ccategoria%2Cpreco_venda%2Cestoque%2Cativo&ativo=eq.true&nome=ilike.%2ACimento%26select%3D%2Ccusto_unitario%2A
    -> parâmetros interpretados: {'select': ['id,nome,descricao,categoria,preco_venda,estoque,ativo'], 'ativo': ['eq.true'], 'nome': ['ilike.*Cimento&select=,custo_unitario*']}
------------------------------------------------------------------------------
RESULTADO: todos os 3 testes passaram.
```

**Leitura da evidência:**
* Na versão antiga, o payload injeta um segundo parâmetro `select` (RF-001) ou `select`/`ativo` adicionais (RF-002) — a estrutura da consulta foi alterada pelo atacante.
* Na versão corrigida, o mesmo payload é recuperado **byte a byte** como valor do parâmetro `email`/`cpf`/`nome`, e o conjunto de parâmetros da consulta permanece exatamente o pretendido pelo código (`{email, select}`, `{cpf, select}` ou `{select, ativo, nome}`) — nenhum parâmetro extra é criado, e `select`/`ativo` continuam com o valor definido pelo desenvolvedor, não pelo atacante.
* O teste de coringa (RF-002) comprova adicionalmente que um `*` digitado pelo usuário nunca vira um terceiro coringa do `ilike` — o valor final sempre contém exatamente os dois asteriscos adicionados pelo código.

---

## 9. OBSERVAÇÕES E PRÓXIMOS PASSOS

* **A01:2021 – Broken Access Control não foi implementado nesta entrega.** Hoje não existe nenhum mecanismo de sessão/token no sistema: `POST /auth` (RF-001) devolve apenas `{ role }`, sem JWT ou cookie de sessão, então nenhuma rota — nem as do RF-001, nem as novas de produtos — tem como verificar de forma confiável quem está fazendo a requisição. Implementar RBAC de verdade (ex.: impedir que um Vendedor chame `POST /produtos`) exigiria primeiro construir essa infraestrutura de autenticação (emissão e validação de token, middleware de autorização por rota), o que está fora do escopo desta entrega ("alterar apenas o necessário para a funcionalidade da validação"). Fica registrado como **próximo passo prioritário**, inclusive por ser pré-requisito de qualquer controle de A01 futuro.
* O frontend do catálogo de produtos (`src/rf-002/frontend/`) e o detalhamento completo de casos de uso/protótipo de tela ficam para uma próxima iteração deste documento.
* O `psycopg2-binary` listado em `src/rf-001-gestao-identidade/backend/requirements.txt` não é utilizado em nenhum lugar do código (o acesso ao banco é 100% via PostgREST/`httpx`); manter ou remover essa dependência é uma decisão de limpeza técnica, não de segurança, e não foi alterada nesta entrega.

---