# DOCUMENTO DE ESPECIFICAÇÃO DE REQUISITOS E ARQUITETURA SEGURA (SSD)
Laboratório de Inovação III — Prof. Edilberto Silva — 2026
VERSÃO 15.0 — COM VALIDAÇÃO AGNÓSTICA DE LINGUAGEM

## 1. METADADOS DO PROJETO E DA EQUIPE

### 1.1 Identificação
NOME_DO_PROJETO: Sistema ERP Construção
DESCRICAO_BREVE: Gestão centralizada de identidade corporativa (IAM) com autenticação JWT/UUID e controle de acesso hierárquico.

### 1.2 Localização dos Artefatos
LINK_REPOSITORIO_GITHUB: https://github.com/Jotajhones/sistema_ERP_LI3_FACSENAC
BRANCH_PRINCIPAL: main
LINK_APLICACAO_DEPLOY: https://sistema-erp-li3-facsenac.onrender.com/
LINK_BANCO_DADOS: Supabase (PostgreSQL)
LINK_DEMONSTRAÇÃO: https://sistema-erp-li-3-facsenac.vercel.app/

### 1.3 Composição da Equipe
(Preencher com a tabela padrão de integrantes do Moodle)

---

## RF-001: AUTENTICAÇÃO E GESTÃO DE IDENTIDADES (IAM)

### 1. IDENTIFICAÇÃO DO REQUISITO

**ID:** RF-001    
**Título:** Autenticação e Gestão de Identidades (IAM)
**Tipo:** Requisito Funcional    
**Prioridade:** ALTA (bloqueia RF-002, RF-003 e RF-004)    
**Complexidade:** MÉDIA (estimado 5 story points)    
**Status:** CONCLUÍDO (Refatorado na Sprint 05)
**Data de Criação:** 27/08/2026    
**Última Atualização:** 09/10/2026    

**Breve Descrição:**
Criar e implementar a gestão de identidade (autenticação e autorização) estabelecendo o núcleo de segurança da API. O sistema emite credenciais criptografadas de acesso e gerencia diferentes tipos de atores corporativos no ERP.

---

### 2. DESCRIÇÃO E ATORES

**Descrição Detalhada e Contexto do Negócio:**
O ERP processa dados sensíveis (orçamentos, produtos e histórico de clientes). É mandatório que exista uma barreira de autenticação central. Vendedores devem logar apenas para gerar orçamentos, enquanto Gestores logam para manipular o catálogo e extrair relatórios.

**Objetivos de Negócio (Benefícios):**
1. Mitigar em 100% o acesso de visitantes anônimos a dados sensíveis de preços de custo e faturamento.
2. Rastrear 100% das ações operacionais do sistema via chave estrangeira (auditoria de autoria).
3. Reduzir a carga administrativa de TI descentralizando o login via portal unificado.

**Atores do Sistema:**

1. **VENDEDOR (Ator Principal)**
Papel: Operar o caixa (PDV).
Permissões:
[ ] CREATE / UPDATE / DELETE (Sem privilégio administrativo).
[X] READ (Autenticação básica via POST `/auth`).

2. **GESTOR / ADMIN (Ator Secundário)**
Papel: Gerenciar recursos da loja.
Permissões:
[X] CREATE, READ, UPDATE, DELETE (Acesso administrativo acoplado na validação de permissões).

3. **SISTEMA (Ator Automático)**
Papel: Emissor e Validador de Credenciais.
Permissões: Leitura da tabela `users` do PostgreSQL para cálculo de hash e comparação criptográfica adaptativa.

---

### 3. ESPECIFICAÇÃO DE CASOS DE USO E REQUISITOS NÃO-FUNCIONAIS

**Caso de Uso (UC-001): Realizar Login no Sistema**

**Pré-Condições**
1. Usuário deve possuir registro ativo na tabela `users`.
2. Conexão estabelecida com a API FastAPI e o banco de dados.

**Pós-Condições (Sucesso)**
1. Acesso concedido e token Bearer válido gerado no navegador.
2. Direcionamento dinâmico efetuado conforme a `user_role`.

**Pós-Condições (Falha)**
1. Acesso bloqueado, devolvendo 401 Unauthorized de forma opaca (sem detalhar se a falha foi no e-mail ou na senha).

**Fluxo Principal**
1. Usuário acessa a página inicial de login (`index.html`).
2. Sistema exibe o formulário com os campos E-mail e Senha.
3. Usuário preenche os campos e aciona o envio.
4. Sistema (Frontend) valida formato do e-mail (Regex) e bloqueia submissões vazias.
5. Sistema (Frontend) dispara `POST /auth`.
6. Sistema (Backend) localiza o usuário pelo e-mail com query serializada.
7. Sistema (Backend) calcula o hash da senha enviada comparando-o com o hash `bcrypt` do banco.
8. Sistema (Backend) retorna HTTP 200 OK com o token da sessão e o perfil.
9. Sistema (Frontend) injeta a credencial no LocalStorage e redireciona ao painel.

**Fluxos Alternativos**
* **A1: Credenciais Inválidas (Falha de Hash/Email):** No passo 7, a senha não coincide (ou o e-mail não existe no banco). O Backend executa cálculo dummy para evitar Timing Attacks e devolve erro 401. Frontend alerta "E-mail ou senha incorretos".
* **A2: Falha na Validação Frontend:** No passo 4, o e-mail está mal formatado. A requisição HTTP é abortada no navegador. O campo é contornado de vermelho exigindo correção.
* **A3: Usuário Desligado/Inativado:** No passo 6, o banco localiza o usuário mas a flag `ativo` está como `false`. O login é liminarmente bloqueado (401), conforme consolidado no RF-005.

**Regras de Negócio (RN)**

| ID | Regra | Descrição |
|---|---|---|
| RN-01 | Entidade Única | O e-mail deve ser chave primária lógica na tabela `users` (UNIQUE). |
| RN-02 | Segurança Zero-Knowledge | Nenhuma senha trafega descriptografada ou é salva em plain text. O uso de `bcrypt` 12 rounds é obrigatório. |
| RN-03 | Respostas Opacas | O sistema jamais informa "E-mail não encontrado". A resposta de falha deve ser uniforme para evitar User Enumeration. |

**Requisitos Não-Funcionais (RNF)**

| ID | Atributo | Requisito | Métrica | Justificativa |
|---|---|---|---|---|
| RNF-01 | Performance | Resolução de Criptografia | Hash check em < 800ms. | O algoritmo deve ser pesado contra força bruta, mas tolerável ao humano. |
| RNF-02 | Escalabilidade | Pico de Logins | Suportar 100 conexões de autenticação/segundo. | Trocas de turno comercial. |
| RNF-03 | Disponibilidade | Uptime IAM | 99% uptime medido via health check. | O ERP morre sem a validação de acesso. |

---

### 4. PROTÓTIPO FUNCIONAL E CÓDIGO (50%)

**Aviso de Evolução de Sprint:**
Conforme as observações de QA do professor, o RF-001 iniciou como esqueleto na Sprint 01 e recebeu sucessivos testes unitários e de integração até o fechamento da Sprint 05. A persistência funcional no deploy oficial e os testes retroativos confirmam a estabilidade total deste módulo primário.

**Mockup Estrutural de Renderização - Frontend Login**
```html
<div class="login-container">
    <form id="loginForm">
        <input type="email" id="email" required placeholder="Email corporativo">
        <input type="password" id="senha" required placeholder="Senha corporativa">
        <button type="submit" id="btnEntrar">Acessar ERP</button>
    </form>
    <div id="feedback-error" class="hidden">Credenciais inválidas.</div>
</div>

```

---

### 5. ARQUITETURA E ADR (15%)

**Diagrama de Componentes**

```text
[ PDV Browser ] ---> POST /auth (Credentials) ---> [ FastAPI Backend ]
                                                       |-- Pydantic Schema Validation
                                                       |-- Bcrypt Check
                                                       v
                                                 [ PostgreSQL ]

```

**ADR-001: PostgreSQL via Supabase para Gestão Relacional**

* **Status:** ACEITO
* **Decisão:** Abandonar o controle de arquivos `.json` ou bancos em memória e adotar Postgres.
* **Consequências:** Integridade referencial total garantida para as colunas de auditoria que dependerão do `user_id` no futuro.

**ADR-002: Bcrypt Adaptativo**

* **Status:** ACEITO
* **Decisão:** Uso do `bcrypt` nativo no backend com `salt` de 12 rounds (`BCRYPT_COST = 12`).
* **Consequências:** Resiliência contra força bruta e Rainbow Tables.

**ADR-003: Validação Dupla (Frontend + Backend)**

* **Status:** ACEITO
* **Decisão:** Validação de RegExp no JS antes de enviar o payload; validação estrutural via `Pydantic` no FastAPI bloqueando dados truncados.

---

### 6. VALIDAÇÃO DE SEGURANÇA OWASP (12%)

**1. A02:2021 – Cryptographic Failures (Hash e Rainbow Tables)**

* **Vulnerabilidade:** Se o banco vazasse, senhas em texto limpo exporiam toda a operação corporativa. Além disso, o servidor poderia sofrer Timing Attack indicando quais e-mails existem.
* **Implementação:** O módulo `security.py` calcula hashes com salt aleatório no ato do cadastro e possui uma função `fake_verify()` que gasta o tempo exato de uma checagem de CPU mesmo quando o e-mail não é encontrado no banco.
* **Teste (Verificação Constante):**

```bash
# Tentativa com email existente e senha errada
time curl -X POST "[http://127.0.0.1:8000/auth](http://127.0.0.1:8000/auth)" -d '{"email":"admin@erp.com","senha":"123"}'
# Tentativa com email falso
time curl -X POST "[http://127.0.0.1:8000/auth](http://127.0.0.1:8000/auth)" -d '{"email":"falso@erp.com","senha":"123"}'

```

*(Ambos retornam HTTP 401 em exatos ~450ms, mascarando a existência de contas no sistema).*

**2. A03:2021 – Injection (Refatoração PostgREST)**

* **Vulnerabilidade:** A rota original montava a URL de busca concatenando `email=eq.{email}`, vulnerável à inserção de chaves HTTP via Payload (Ex: `email=vendedor@erp.com&select=*,password`).
* **Implementação:** Conforme homologado retroativamente na Sprint 02, o repositório adotou `build_safe_query(quote_via=quote)`. O framework escapa caracteres como `&` e `=` para formato `%26` e `%3D`.
* **Teste (Isolamento de Entrada):**

```bash
curl -X POST "[http://127.0.0.1:8000/auth](http://127.0.0.1:8000/auth)" \
     -H "Content-Type: application/json" \
     -d '{"email": "vendedor@erp.com&select=*,password_hash", "senha": "abc"}'

```

*(Status Retornado: 401 Unauthorized. O servidor PostgreSQL processou literalmente a string "vendedor@erp.com&select=*,password_hash", não encontrando o e-mail. Nenhuma coluna oculta vazou).*

**3. A05:2021 – Security Misconfiguration (CORS e Secrets)**

* **Vulnerabilidade:** Cabeçalhos `allow_origins=["*"]` e chaves expostas no código abririam a rede a acessos via exploits rodando em outros sites (CSRF).
* **Implementação:** Refatorado em sprints subsequentes: as rotas aceitam requisições estritamente de `localhost`, `vercel.app` e `onrender.com`. Além disso, a credencial do DB usa `python-dotenv`.
* **Teste:**

```bash
curl -X OPTIONS "[http://127.0.0.1:8000/auth](http://127.0.0.1:8000/auth)" \
     -H "Origin: [http://malicioso.com](http://malicioso.com)" \
     -H "Access-Control-Request-Method: POST" -I

```

*(A resposta bloqueia o CORS, não informando cabeçalhos `Access-Control-Allow-Origin` para o site pirata).*

