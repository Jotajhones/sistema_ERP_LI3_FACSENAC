### RF-003: GESTÃO DE ORÇAMENTOS E RECEBIMENTO DE ESTOQUE (COM CONTROLE RBAC)

---

## 1. IDENTIFICAÇÃO DO REQUISITO 

**ID:** RF-003  
**Título:** Gestão de Orçamentos Rápidos, Recebimento de Lotes e Controle de Acesso (RBAC)  
**Tipo:** Requisito Funcional  
**Prioridade:** ALTA (Core business para faturamento e gestão física de estoque)  
**Complexidade:** ALTA (estimado 13 story points / 8 micro-cards executados em Squad)  
**Status:** CONCLUÍDO (Entregue na Sprint 3)  
**Data de Criação:** 08/09/2012  
**Última Atualização:** 08/09/2012  

**Breve Descrição:**
O sistema deve permitir a geração de orçamentos flexíveis (com busca automática de CPF, cadastro silencioso ou modo anônimo) e o registro de entrada de mercadorias em grandes volumes (paletes/lotes). Toda a interface e os endpoints devem ser estritamente controlados por funções RBAC (Role-Based Access Control) para impedir ações administrativas por vendedores, garantindo ainda o encerramento real da sessão no banco de dados (Logout).

---

## 2. DESCRIÇÃO E ATORES 

**Contexto do Negócio:**
O fluxo de uma loja de materiais de construção exige agilidade no balcão e segurança na retaguarda. Vendedores não podem perder tempo em telas complexas de cadastro de clientes para emitir um simples orçamento. Simultaneamente, recebimentos físicos chegam em grandes volumes (ex: um caminhão de areia, um palete de cimento), exigindo uma estrutura de banco que suporte entrada de lotes. Tudo isso deve estar blindado: o vendedor opera a venda, mas apenas o gestor manipula o catálogo, os preços e o estoque.

**Atores do Sistema:**

### 1. VENDEDOR (Ator Principal)

* **Papel:** Operador de caixa/balcão que atende o cliente final.
* **Responsabilidade:** Gerar orçamentos rápidos e consultar o catálogo.
* **Permissões:**
* CREATE (Orçamentos, Clientes via cadastro silencioso).
* READ (Catálogo de produtos, clientes próprios).
* UPDATE / DELETE (Bloqueado visualmente no front e via injeção de dependência no back).



### 2. GESTOR / ADMIN (Ator Secundário)

* **Papel:** Administrador da loja.
* **Responsabilidade:** Cadastrar produtos, atualizar preços, registrar entrada de lotes no estoque e inativar itens.
* **Permissões:**
* CREATE, READ, UPDATE, DELETE em todas as entidades.



### 3. CLIENTE (Ator Passivo)

* **Papel:** Recebedor do orçamento gerado.

### 4. SISTEMA (Ator Automático)

* **Papel:** Executor de regras de segurança e banco.
* **Responsabilidade:** Validar as permissões de rota (AuthZ), executar o cadastro silencioso em background e destruir fisicamente o token de sessão na tabela `sessoes` durante o logout.
* **Permissões:**
* Todas as operações requeridas internamente.



---

## 3. ESPECIFICAÇÃO DE CASOS DE USO E REQUISITOS NÃO-FUNCIONAIS 

**Caso de Uso (UC-003): Gerar Orçamento com Cadastro Silencioso e RBAC**

### Pré-Condições

* Vendedor autenticado com token válido.
* Produtos devidamente cadastrados com `quantidade_estoque`.
* Utilitário `rbac.js` ativo, ocultando opções de gestão na UI.

### Pós-Condições (Sucesso)

* Orçamento registrado.
* Cliente cadastrado silenciosamente no banco (caso CPF seja novo).
* Sessão mantida segura sem elevação de privilégios.

### Pós-Condições (Falha)

* Vendedor tentando acionar endpoints de Gestor recebe 403 Forbidden.
* Falha na API não bloqueia o fluxo de limpeza de dados no momento do Logout.

### Fluxo Principal (Geração de Orçamento)

1. Vendedor acessa a tela "Novo Orçamento".
2. Vendedor digita o CPF do cliente no campo de busca.
3. Sistema dispara `GET /pessoas/{cpf}`.
4. Sistema não encontra o cliente (Retorno 404 silencioso) e habilita o campo "Nome" para digitação livre.
5. Vendedor preenche o "Nome" do cliente e adiciona os produtos ao carrinho.
6. Vendedor clica em "Salvar Orçamento".
7. Sistema (Frontend) dispara paralelamente `POST /pessoas` com o Nome/CPF para efetuar o Cadastro Silencioso em background.
8. Sistema captura o ID do cliente recém-criado.
9. Sistema dispara `POST /orcamentos` vinculando os produtos e o novo ID do cliente.
10. Sistema exibe "Orçamento salvo com sucesso".

### Fluxo Alternativo A1: Cliente Já Cadastrado

* 3a.1. Ao buscar o CPF, a API retorna `200 OK` com os dados.
* 3a.2. Frontend autopreenche o Nome do cliente e bloqueia edição.
* 3a.3. O fluxo segue diretamente para a adição de itens e salvamento da OS.

### Fluxo Alternativo A2: Orçamento Anônimo

* 2a.1. Vendedor deixa o campo CPF em branco.
* 2a.2. O botão "Buscar" é ignorado.
* 2a.3. Ao salvar, o sistema processa o orçamento vinculando-o a um ID genérico de "Consumidor Final" (ou cliente nulo).

### Fluxo Alternativo A3: Recebimento de Lote de Estoque (Apenas Gestor)

* 1. Gestor clica no botão "Receber Lote" (botão invisível para vendedores via `rbac.js`).


* 2. Gestor informa a `quantidade_recebida` (ex: 150 sacos de cimento).


* 3. Sistema dispara `PATCH /produtos/{id}/recebimento`.


* 4. API valida a role do token no banco (AuthZ).


* 5. API soma a quantidade ao estoque atual e registra auditoria.



### Regras de Negócio (RN)

| ID | Regra | Descrição |
| --- | --- | --- |
| **RN-01** | Recebimento Positivo | A rota de entrada de lote só aceita `quantidade_recebida` > 0. Retorna 422 em caso de erro. |
| **RN-02** | Autorização Restrita (API) | Rotas `POST/PUT/DELETE/PATCH` de produtos operam com injeção de dependência estrita, aceitando apenas roles `ADMIN` ou `GESTOR`. |
| **RN-03** | Interface de Menor Privilégio | O `rbac.js` esconde botões com `data-role="admin-only"` caso o usuário não seja gestor. |
| **RN-04** | Sessão Volátil | O Logout agora envia um `POST /auth/logout` que inativa ou deleta fisicamente o UUID da tabela `sessoes`. |
| **RN-05** | Tolerância a Falhas no Logout | Se o `POST /auth/logout` falhar (API offline), o front-end garante a exclusão obrigatória do Token no LocalStorage (Fail-safe). |
| **RN-06** | UX sem Interrupção | O erro 404 na busca do CPF não emite alerta em tela; serve apenas de gatilho para o cadastro silencioso. |

### Requisitos Não-Funcionais (RNF)

| ID | Atributo | Requisito | Métrica | Justificativa |
| --- | --- | --- | --- | --- |
| **RNF-01** | Segurança | RBAC Server-side | Nenhuma mutação sem role validada | Frontend não é ambiente seguro para travar requisições. |
| **RNF-02** | Usabilidade | Feedback dinâmico | Autocomplete instantâneo | Rapidez exigida no balcão de vendas da loja. |
| **RNF-03** | Idempotência | Logout Seguro | Retornar 200 mesmo sem sessão | Evita loops infinitos ou quebras ao deslogar. |

---

## 4. PROTÓTIPO FUNCIONAL 

**Mockup - Tela 1: Orçamento - Busca de CPF**

```
┌────────────────────────────────────────────────┐
│  ☰ ERP Construção   |   Vendedor Logado        │
├────────────────────────────────────────────────┤
│                                                │
│  📝 Novo Orçamento                             │
│                                                │
│  CPF do Cliente (Opcional):                    │
│  [ 000.000.000-00 ] [ 🔍 BUSCAR ]              │
│                                                │
│  Nome:                                         │
│  [ (Bloqueado. Informe o CPF ou Pule) ]        │
│                                                │
│  [ AVANÇAR SEM CLIENTE ]                       │
└────────────────────────────────────────────────┘

```

**Mockup - Tela 2: Orçamento - Cadastro Silencioso (Após Erro 404)**

```
┌────────────────────────────────────────────────┐
│  ☰ ERP Construção   |   Vendedor Logado        │
├────────────────────────────────────────────────┤
│                                                │
│  📝 Novo Orçamento - Cliente Novo              │
│                                                │
│  CPF do Cliente: [ 123.456.789-00 ] ✅         │
│                                                │
│  Nome:                                         │
│  [ Maria de Fátima (Campo Liberado)  ]         │
│                                                │
│  [ PRODUTOS ▼ ]                                │
│  + 1x Cimento CP II 50kg                       │
│                                                │
│  [ SALVAR ORÇAMENTO ] (Executa os 2 POSTs)     │
└────────────────────────────────────────────────┘

```

**Mockup - Tela 3: Catálogo - Visão do VENDEDOR (RBAC Ativo)**

```
┌────────────────────────────────────────────────┐
│  📦 Catálogo Geral                             │
│                                                │
│  NOME               | UN.  | ESTOQUE | PREÇO   │
│  Cimento CP II 50kg | Saco | 150     | R$ 35   │
│  Areia Média        | M3   | 40      | R$ 90   │
│                                                │
│  (Botão '+ Novo Produto' foi removido pelo     │
│   rbac.js. Coluna 'Ações' inativada)           │
└────────────────────────────────────────────────┘

```

**Mockup - Tela 4: Catálogo - Visão do GESTOR (RBAC Ativo)**

```
┌────────────────────────────────────────────────┐
│  📦 Catálogo Geral       [ + NOVO PRODUTO ]    │
│                                                │
│  NOME               | ESTOQUE | AÇÕES          │
│  Cimento CP II 50kg | 150     | [✏️] [📥 LOTE]  │
│                                                │
│  [📥 LOTE] -> Dispara PATCH /produtos/1/receb  │
└────────────────────────────────────────────────┘

```

---

## 5. ARQUITETURA E ADR 

### Diagrama de Componentes (Foco em RBAC e Sessions)

```
[ Frontend (Vanilla JS) ] 
  |-- rbac.js (Oculta botões baseado na role local)
  |-- erpFetch (Anexa Bearer Token)
  |
  +-- /auth/logout -------------------> [ FastAPI Backend ]
  +-- /produtos (POST/PUT/PATCH) ----->   |-- Dependência `RequireRole(['GESTOR'])`
  +-- /pessoas (POST silencioso) ----->   |-- Consulta Tabela `sessoes`
                                          |
                                      [ Banco PostgreSQL / Supabase ]
                                          |-- tb_produtos (Com quantidade_estoque, unidade_medida)

```

### ADR-009: Injeção de Dependência RBAC no FastAPI

**Status:** ACEITO
**Contexto:** Garantir que requisições forçadas fora da UI não executem mutações no banco.
**Decisão:** Criação da classe `require_role(["ADMIN", "GESTOR"])` instanciada dentro de um `Depends()` nas rotas sensíveis do FastAPI.
**Consequências:** Bloqueia bypass de frontend (403 Forbidden). Segurança total da regra de negócio de estoque.

### ADR-010: Controle de Acesso no Client-Side (Vanilla JS)

**Status:** ACEITO
**Contexto:** Evitar que botões inacessíveis poluam a tela do Vendedor.
**Decisão:** Importação global do script utilitário `rbac.js` que aplica `display: none` a qualquer elemento HTML com `data-role="admin-only"` caso o `localStorage.userRole` seja `VENDEDOR`.
**Consequências:** UX aprimorada; mitigação visual rápida sem frameworks complexos.

### ADR-011: Encerramento Físico de Sessão (Logout)

**Status:** ACEITO
**Contexto:** Prevenir uso de tokens velhos interceptados.
**Decisão:** Criação de rota explícita `POST /auth/logout` que deleta a linha do UUID correspondente na tabela `sessoes`.
**Consequências:** Fim do ciclo de vida da sessão realçada no backend.

### ADR-012: Cadastro Silencioso vs Explícito

**Status:** ACEITO
**Contexto:** Minimizar atrito no balcão de vendas.
**Decisão:** Orquestrar chamadas de `POST /pessoas` no frontend logo antes do salvamento da OS, ao invés de forçar o usuário a mudar de tela para "Cadastrar Cliente".
**Consequências:** Alta velocidade operacional; complexidade levemente transferida para o front-end.

---

## 6. VALIDAÇÃO DE SEGURANÇA OWASP

### A05:2021 – Security Misconfiguration (Configuração Incorreta de Segurança)

**Vulnerabilidade:**
Nas sprints passadas, para facilitar o desenvolvimento inicial, o backend foi configurado com CORS (Cross-Origin Resource Sharing) excessivamente permissivo, permitindo solicitações vindas de qualquer domínio da internet (`allow_origins=["*"]`). Isso abria brechas para ataques de Cross-Site Request Forgery (CSRF) e conexões maliciosas orquestradas por domínios de terceiros.

**Implementação:**
A falha foi mitigada no arquivo de inicialização do FastAPI (`main.py`). O wildcard `"*"` foi estritamente substituído pela lista branca de domínios confiáveis do projeto: apenas os deploys oficiais da aplicação e o ambiente de desenvolvimento local (localhost) possuem autorização de acesso ao backend.

**Código-fonte (Proteção Aplicada):**

```python
# src/rf-00X-backend/main.py
from fastapi.middleware.cors import CORSMiddleware

# Lista restrita e explícita de origens permitidas
ORIGENS_PERMITIDAS = [
    "http://localhost:3000",
    "http://127.0.0.1:5500",
    "https://erp-construcao.vercel.app" 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENS_PERMITIDAS,  # Remoção do wildcard perigoso
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

```

**Teste de Segurança Documentado:**
Foi executado um teste de invasão (Simulação de Origem Incorreta) utilizando o Postman.

1. Ao enviar um `GET /produtos` com o cabeçalho HTTP `Origin: [https://site-hacker.com.br](https://site-hacker.com.br)`, o servidor rejeita o pre-flight (OPTIONS), bloqueando a visualização e a mutação dos dados com a resposta de restrição CORS no header.
2. Comprovou-se que apenas as chamadas disparadas pelo frontend oficial (`[https://erp-construcao.vercel.app](https://erp-construcao.vercel.app)`) são aceitas.

