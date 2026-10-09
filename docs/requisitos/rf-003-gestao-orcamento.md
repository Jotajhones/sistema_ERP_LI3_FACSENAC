# DOCUMENTO DE ESPECIFICAÇÃO DE REQUISITOS E ARQUITETURA SEGURA (SSD)
Laboratório de Inovação III — Prof. Edilberto Silva — 2026
VERSÃO 15.0 — COM VALIDAÇÃO AGNÓSTICA DE LINGUAGEM

## 1. METADADOS DO PROJETO E DA EQUIPE

### 1.1 Identificação
NOME_DO_PROJETO: Sistema ERP Construção
DESCRICAO_BREVE: Sistema B2B para gestão completa de catálogo, orçamentos, estoque e conversão em faturamento para lojas de materiais de construção.

### 1.2 Localização dos Artefatos
LINK_REPOSITORIO_GITHUB: https://github.com/Jotajhones/sistema_ERP_LI3_FACSENAC
BRANCH_PRINCIPAL: main
LINK_APLICACAO_DEPLOY: https://sistema-erp-li3-facsenac.onrender.com/
LINK_BANCO_DADOS: Supabase (PostgreSQL)
LINK_DEMONSTRAÇÃO: https://sistema-erp-li-3-facsenac.vercel.app/

### 1.3 Composição da Equipe
| ID | Nome Completo | Papel Primário | Papel Secundário | E-mail / Contato |
|---|---|---|---|---|
| 1 | João Pedro de Lima | Product Owner | Tech Lead / DevOps | joao52517876@edu.df.senac.br |
| 2 | Miguel Nunes | Desenvolvedor Back-End | Full Stack | miguel59970766@edu.df.senac.br |
| 3 | Luciano Santos | Desenvolvedor Back-End | Full Stack  | luciano58995256@edu.df.senac.br |
| 4 | Daniel Silva | DBA / Banco de Dados | Full Stack  | daniel52370026@edu.df.senac.br |
| 5 | Arthur Andrade | Desenvolvedor Front-End | Full Stack  | arthur59275206@edu.df.senac.br |
| 6 | Pedro Soares| Desenvolvedor Front-End | Full Stack  | pedro59153296@edu.df.senac.br |
| 7 | Matheus Chagas | AppSec / QA | Full Stack | matheus57119256@edu.df.senac.br |

---

## RF-003: GESTÃO DE ORÇAMENTOS E RECEBIMENTO DE ESTOQUE

### 1. IDENTIFICAÇÃO DO REQUISITO

**ID:** RF-003
**Título:** Gestão de Orçamentos Rápidos, Persistência e Controle de Acesso (RBAC)
**Tipo:** Requisito Funcional
**Prioridade:** ALTA (Core business para faturamento e gestão física de estoque)
**Complexidade:** ALTA (estimado 13 story points)
**Status:** CONCLUÍDO
**Data de Criação:** 08/09/2026
**Última Atualização:** 09/10/2026

**Breve Descrição:**
O sistema deve permitir a geração e persistência de orçamentos flexíveis (com busca automática de CPF ou modo anônimo) e o registro de itens no banco de dados. Toda a interface e os endpoints devem ser estritamente controlados por funções RBAC (Role-Based Access Control) para impedir acesso administrativo por vendedores.

---

### 2. DESCRIÇÃO E ATORES

**Descrição Detalhada e Contexto do Negócio:**
O fluxo de uma loja de materiais de construção exige agilidade no balcão e segurança na retaguarda transacional. Vendedores precisam emitir orçamentos sem fricção na interface, enquanto o sistema garante a persistência ACID no backend. 

**Objetivos de Negócio (Benefícios):**
1. Reduzir o tempo médio de atendimento no balcão em 40% através da busca unificada de CPF.
2. Garantir 100% de integridade transacional na conversão de orçamentos, evitando vendas sem estoque.
3. Prevenir fraudes financeiras limitando a alteração de preços estruturais apenas a Gestores.

**Atores do Sistema:**

1. **VENDEDOR (Ator Principal)**
Papel: Operador de caixa/balcão que atende o cliente final.
Permissões:
[X] CREATE (Criar orçamentos e clientes de balcão).
[X] READ (Ler produtos e próprios orçamentos).
[ ] UPDATE (Apenas dados de clientes sem vínculo funcional).
[ ] DELETE (Bloqueado).

2. **GESTOR / ADMIN (Ator Secundário)**
Papel: Administrador da loja e do estoque.
Permissões:
[X] CREATE, READ, UPDATE, DELETE (Acesso administrativo completo).

3. **SISTEMA (Ator Automático)**
Papel: Validador de integridade e sessão.
Permissões: Todas as operações lógicas do banco de dados (validação AuthZ, controle de trigger de estoque).

---

### 3. ESPECIFICAÇÃO DE CASOS DE USO E REQUISITOS NÃO-FUNCIONAIS

**Caso de Uso (UC-003): Gerar e Persistir Orçamento**

**Pré-Condições**
1. Vendedor autenticado com token JWT ativo.
2. Produtos cadastrados na tabela com `quantidade_estoque` superior a zero.
3. Banco de dados PostgreSQL online e respondendo a conexões.

**Pós-Condições (Sucesso)**
1. Orçamento persistido nas tabelas `orcamentos` e `orcamento_itens`.
2. Cliente cadastrado silenciosamente caso o CPF seja inédito.
3. Resposta HTTP 201 Created retornada ao frontend com o ID gerado.

**Pós-Condições (Falha)**
1. Transação abortada (Rollback) caso haja inconsistência de dados.
2. Vendedor recebe HTTP 403 Forbidden caso tente usar rotas de Gestor.

**Fluxo Principal**
1. Vendedor acessa a tela "Novo Orçamento".
2. Vendedor digita o CPF do cliente no campo de busca.
3. Sistema dispara `GET /pessoas/{cpf}`.
4. Sistema não encontra o cliente (404 silencioso) e habilita o campo "Nome" para digitação livre.
5. Vendedor preenche o Nome e adiciona produtos ao carrinho validando quantidades.
6. Vendedor clica em "Salvar Orçamento".
7. Sistema (Frontend) dispara `POST /pessoas` efetuando o cadastro em background.
8. Sistema captura o ID do cliente recém-criado.
9. Sistema (Frontend) dispara `POST /orcamentos` com a lista de itens.
10. Sistema (Backend) valida a role via `Depends(get_current_user)`.
11. Sistema (Backend) recalcula o valor total via server-side para evitar fraudes de interface.
12. Sistema (Backend) persiste os dados nas tabelas `orcamentos` e `ordens_servico_itens` usando bulk insert.
13. Sistema exibe confirmação visual de sucesso na interface.

**Fluxos Alternativos**
* **A1: Cliente Já Cadastrado:** No passo 3, a API retorna 200 OK. O frontend autopreenche o Nome do cliente, bloqueia a edição do campo e o fluxo salta para o passo 5.
* **A2: Orçamento Anônimo:** No passo 2, o vendedor deixa o CPF em branco. No passo 9, a API recebe o payload com `cliente_id` nulo, persistindo a venda como "Consumidor Final".
* **A3: Recebimento de Lote de Estoque (Apenas Gestor):** O Gestor clica em "Receber Lote". O sistema dispara `PATCH /produtos/{id}/recebimento`. A API valida o perfil (GESTOR) e incrementa a `quantidade_estoque` no banco, registrando a operação.

**Regras de Negócio (RN)**

| ID | Regra | Descrição |
|---|---|---|
| RN-01 | Matemática Server-Side | O backend deve recalcular Preço x Quantidade independentemente do valor submetido pelo frontend para prevenir fraudes. |
| RN-02 | Autorização Restrita (API) | Rotas de mutação estrutural exigem injeção de dependência estrita (`RequireRole(['ADMIN', 'GESTOR'])`). |
| RN-03 | UX sem Interrupção | O erro 404 na busca do CPF não emite alerta em tela; atua apenas como gatilho para o cadastro em background. |
| RN-04 | Bulk Insert Otimizado | Múltiplos itens de um mesmo orçamento devem ser gravados em uma única transação no banco. |
| RN-05 | Sessão Volátil | O encerramento da sessão deve enviar um `POST /auth/logout` que deleta fisicamente o UUID da tabela `sessoes`. |
| RN-06 | Tolerância a Falhas | Se a API de logout estiver offline, o frontend realiza a exclusão mandatória do Token no LocalStorage. |

**Requisitos Não-Funcionais (RNF)**

| ID | Atributo | Requisito | Métrica | Justificativa |
|---|---|---|---|---|
| RNF-01 | Performance | Baixa latência em inserções. | Tempo de resposta < 800ms para geração de orçamentos com até 20 itens. | Agilidade no balcão de vendas. |
| RNF-02 | Escalabilidade | Suporte a acessos concorrentes. | Suportar 100 requisições simultâneas sem deadlocks no banco. | Garantir operação em horário de pico. |
| RNF-03 | Segurança | RBAC estrito via API. | 100% das rotas de mutação protegidas por validação JWT/UUID. | Frontend não é ambiente seguro. |

---

### 4. PROTÓTIPO FUNCIONAL E CÓDIGO 

**Arquitetura de Arquivos Entregues:**
```text
src/rf-003-gestao-orcamento/
├── backend/
│   ├── routers/orcamentos_router.py
│   ├── services/orcamentos_service.py
│   ├── schemas/orcamentos_schema.py
│   └── repositories/orcamentos_repository.py
├── frontend/
│   ├── listarOrcamento/
│   │   ├── app.js
│   │   ├── listarOrcamento.css
│   │   └── listarOrcamento.html
│   └── scripts/
│       ├── ordemServico.js
│       └── rbac.js
└── database/ddl/rf-003-orcamentos-ddl.sql