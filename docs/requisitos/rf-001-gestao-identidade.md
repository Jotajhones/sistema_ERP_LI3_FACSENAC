### RF-001: Autenticação e Gestão de Identidades (IAM)

---

## 1. IDENTIFICAÇÃO DO REQUISITO

**ID:** RF-001
**Título:** Gestão de identidades
**Tipo:** Requisito Funcional
**Prioridade:** ALTA (bloqueia RF-002, RF-003 e RF-004)
**Complexidade:** MÉDIA (estimado 5 story points)
**Status:** EM DESENVOLVIMENTO
**Data de Criação:** 27/08/2026
**Última Atualização:** 27/08/2026

**Breve Descrição:**
Criar e implementar gestão de identidade (autenticação e autorização) para diferenciar e administrar diferentes tipos de usuários no sistema. O sistema deve permitir que um usuário qualquer devidamente cadastrado consiga com suas credenciais logar e permanecer logado, bem como verificar se as credenciais são válidas.

---

## 2. DESCRIÇÃO E ATORES

**Contexto do negócio:**
O sistema precisa que um vendedor consiga logar para criar OS e/ou fazer orçamentos para clientes. Um gestor precisa logar para gerar relatórios sobre quantas compras foram realizadas e quem está conseguindo fechar mais vendas.

**Atores do Sistema:**

### 1. User comum (vendedor) - Ator Principal

* **Papel:** Acessar o sistema para criar ordens de serviço (OS) e orçamentos.
* **Permissões:**
* READ (Visualizar produtos e próprios orçamentos).
* CREATE (Gerar orçamentos e OS).



### 2. Administrador (gestor) - Ator Secundário

* **Papel:** Gerar relatórios financeiros e gerenciar a equipe.
* **Permissões:**
* CREATE, READ, UPDATE, DELETE (Acesso administrativo completo).



### 3. Sistema - Ator Secundário

* **Papel:** Validar credenciais, checar autorização de rotas e conectar-se ao banco de dados.
* **Permissões:**
* Todas as operações internas requeridas pelas rotas.



---

## 3. ESPECIFICAÇÃO DE CASOS DE USO E REQUISITOS NÃO-FUNCIONAIS

**Caso de Uso (UC-001): Realizar Login no Sistema**

### Pré-Condições

* Usuário deve possuir cadastro prévio ativo no banco de dados.
* Conexão estabelecida com a API e o banco de dados.

### Pós-Condições (Sucesso)

* Acesso concedido e interface carregada conforme a role do usuário.
* Sessão/cabeçalho de autorização ativado no navegador.

### Pós-Condições (Falha)

* Acesso negado com mensagem de erro visual por meio de um alert.
* Registro da tentativa falha nos logs de segurança.

### Fluxo Principal

1. Usuário acessa a página inicial de login.
2. Sistema exibe o formulário com os campos "E-mail" e "Senha".
3. Usuário preenche os campos e clica no botão de acesso.
4. Sistema (Frontend) executa função booleana para validar o formato do e-mail e garantir que a senha não está vazia.
5. Sistema (Frontend) envia requisição POST para o endpoint `/auth` da API.
6. Sistema (Backend) busca o usuário pelo e-mail no banco de dados Postgres.
7. Sistema (Backend) compara a senha informada com o hash bcrypt armazenado.
8. Sistema (Backend) retorna o status HTTP 200 OK contendo a `user_role`.
9. Sistema (Frontend) exibe alert informando a resposta da API e redireciona para o painel.

### Fluxo Alternativo A1: Credenciais Inválidas

* 7a.1. O hash gerado pela senha informada não coincide com o do banco, ou o e-mail não existe.
* 7a.2. Backend retorna erro HTTP 401 (Unauthorized).
* 7a.3. Frontend exibe alert: "E-mail ou senha incorretos".
* 7a.4. Campos são limpos.

### Fluxo Alternativo A2: Erro de Validação no Frontend

* 4a.1. A função booleana identifica que o formato do e-mail está incorreto ou a senha está vazia.
* 4a.2. O envio da requisição para a API é bloqueado.
* 4a.3. Frontend alerta sobre a necessidade de preenchimento válido.

### Regras de Negócio (RN)

| ID | Regra | Descrição |
| --- | --- | --- |
| **RN-01** | E-mail Único | E-mail deve ser único no sistema; não permitir duplicatas. |
| **RN-02** | Separação de Entidade | A tabela `users` deve conter o e-mail, hash de senha e role, possuindo relação 1:1 com a tabela `pessoas`. |
| **RN-03** | Criptografia Obrigatória | Nenhuma senha pode ser armazenada em texto limpo; uso obrigatório de bcrypt no banco de dados. |

### Requisitos Não-Funcionais (RNF)

| ID | Atributo | Requisito | Métrica | Justificativa |
| --- | --- | --- | --- | --- |
| **RNF-01** | Performance | Resposta em <2 segundos. | Tempo médio de resposta. | UX: usuário não fica esperando. |
| **RNF-02** | Escalabilidade | Suportar 100+ usuários simultâneos. | Conexões concorrentes. | Loja pode ter múltiplas requisições simultâneas. |
| **RNF-03** | Disponibilidade | 99% uptime em produção. | SLA medido. | Negócio depende da aplicação. |

---

## 4. PROTÓTIPO FUNCIONAL

**Mockup - Tela 1: Formulário Vazio (Estado Inicial)**

```text
┌────────────────────────────────────────────────┐
│   ERP Construção - Acesso Restrito             │
├────────────────────────────────────────────────┤
│                                                │
│  E-mail: [_________________________]           │
│  Senha:  [_________________________]           │
│                                                │
│  [ ENTRAR ]                                    │
│                                                │
└────────────────────────────────────────────────┘

```

**Mockup - Tela 2: Erro de Validação Booleana**

```text
┌────────────────────────────────────────────────┐
│   ERP Construção - Acesso Restrito             │
├────────────────────────────────────────────────┤
│                                                │
│  E-mail: [joao.pedro               ]           │
│  (X) E-mail em formato inválido                │
│  Senha:  [********                 ]           │
│                                                │
│  [ ENTRAR ] (Bloqueado)                        │
│                                                │
└────────────────────────────────────────────────┘

```

---

## 5. ARQUITETURA E ADR

### Diagrama de Componentes

```text
[Frontend (HTML5 + CSS3 + JS Vanilla)] ---> Fetch API (JSON) ---> [Backend (Python/FastAPI)] ---> [Banco (PostgreSQL/Supabase)]

```

### ADR-001: PostgreSQL (Supabase) como Banco de Dados

* **Contexto:** O sistema ERP requer forte integridade relacional para lidar com tabelas separadas de autenticação e dados de negócio.
* **Decisão:** Utilizar PostgreSQL hospedado no Supabase.
* **Consequências:** Escalabilidade relacional garantida, sem a necessidade de provisionamento local de servidores por parte da equipe.

### ADR-002: Python com API REST para o Backend

* **Contexto:** Necessidade de construir uma API de forma ágil com uma equipe iniciante.
* **Decisão:** Utilizar o framework FastAPI ou Flask em Python para prover o endpoint `/auth`.
* **Consequências:** Curva de aprendizado menor para a equipe de backend responsável pela criação das rotas e integração com o banco.

### ADR-003: Vanilla JS (HTML5+CSS3+JS) para o Frontend

* **Contexto:** A equipe front-end possui nível iniciante, tornando frameworks robustos um risco para a entrega do protótipo funcional.
* **Decisão:** Uso de JavaScript Vanilla, separando a função booleana de validação da chamada da API via `fetch()`.
* **Consequências:** Código mais simples, fácil depuração e execução direta no navegador sem necessidade de build steps.

---

## 6. DADOS DE TESTE (SEEDS)

Para o ambiente de desenvolvimento, o banco de dados é populado com usuários padrão para facilitar os testes de integração entre o Frontend e a API.

> **Atenção (Frontend):** Todos os e-mails listados abaixo utilizam a mesma senha de acesso: `senha123`.

* **ADMIN:** `admin@erp.com`
* **GESTOR:** `gestor@erp.com`
* **VENDEDOR:** `vendedor@erp.com`
* **CLIENTE:** `cliente@erp.com`
