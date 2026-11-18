# DOCUMENTO DE ESPECIFICAÇÃO DE REQUISITOS E ARQUITETURA SEGURA (SSD)

Laboratório de Inovação III — Prof. Edilberto Silva — 2026
VERSÃO 16.3 — COM VALIDAÇÃO AGNÓSTICA DE LINGUAGEM

## 1. METADADOS DO PROJETO E DA EQUIPE

### 1.1 Identificação

- **ID:** RF-007  
- **Título:** Recuperação de Orçamentos Pendentes e Tracking de Contato  
- **Tipo:** Requisito Funcional
- **Prioridade:** Alta  
- **Complexidade:** 5 story points  

### 1.2 Localização dos Artefatos (URLs Obrigatórias)

- **a) URL da Aplicação (Deploy Online):** https://sistema-erp-li-3-facsenac.vercel.app/ (Frontend Hospedado na Vercel)
- **b) Link do Banco de Dados Online:** https://supabase.com/dashboard/project/qlfjdnljfmicjkrbrwih/editor/ (Leitura para prof.edilberto.silva@gmail.com)
- **c) Link do GitHub (Repositório):** https://github.com/Jotajhones/sistema_ERP_LI3_FACSENAC (Branch: main)

*(Nota de Infraestrutura: A API Backend opera sob o domínio https://sistema-erp-li3-facsenac.onrender.com).*

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

## 2. DESCRIÇÃO E ATORES  

O requisito de Recuperação de Orçamentos permite que os vendedores do sistema ERP filtrem proativamente orçamentos que foram gerados, mas que ainda não foram convertidos em Ordens de Serviço (vendas reais). A funcionalidade atua como um mini-CRM inserido na própria listagem de orçamentos do balcão.

Através de uma integração leve via link direto web, o sistema higieniza o telefone do cliente, codifica os dados mercadológicos e aciona o WhatsApp Web/Desktop do operador comercial, pré-formatando uma mensagem de resgate da venda. A abordagem dispensa a contração de APIs oficiais caras e onerosas, focando no esforço manual assistido pelo frontend.

Para garantir a rastreabilidade (tracking) sem inflar ou corromper as tabelas financeiras de orçamentos, o sistema cria um registro em uma tabela associativa (`orcamentos_contatos`) de forma reativa assim que o vendedor retorna o foco para a tela do ERP. Isso garante que a gestão saiba quais orçamentos foram acompanhados e qual vendedor realizou o esforço de recuperação, evitando sobreposição de contatos.

### Benefícios para o Negócio  
- Aumentar a taxa de conversão de orçamentos abandonados através de contato proativo estruturado.  
- Evitar conflito comercial, impedindo que dois vendedores entrem em contato com o mesmo cliente.  
- Gerar métricas de engajamento da equipe comercial, registrando a autoria das ações sem ferir dados contábeis.

### Atores

#### Vendedor
- **Papel:** Operador responsável por contatar o cliente.  
- **Permissões:** READ (orçamentos pendentes), CREATE (registro de contato).  

#### Gestor / Admin
- **Papel:** Auditor de desempenho.  
- **Permissões:** READ (Auditar acompanhamentos globais).  

#### Sistema (Automático)
- **Papel:** Formatador URI e Provedor AuthZ.  
- **Permissões:** Inferência do ID do vendedor via Token JWT e registro blindado no banco de dados.  

---

## 3. CASOS DE USO E REQUISITOS NÃO-FUNCIONAIS

### Fluxo Principal: Contatar Cliente e Registrar Ação

**Pré-condições:**
- Usuário autenticado com perfil VENDEDOR ou GESTOR.  
- Cliente do orçamento possui telefone cadastrado.  
- Orçamento possui status PENDENTE no banco de dados.  

**Fluxo:**
1. Vendedor seleciona o filtro "Não Contatados" na tela de Orçamentos.  
2. Backend realiza o cruzamento de dados, retornando apenas orçamentos sem registro na tabela de contatos.  
3. Sistema exibe a lista filtrada com ícone de WhatsApp.  
4. Vendedor clica no ícone de contato de um orçamento específico.  
5. Frontend extrai nome do cliente, nome do vendedor, telefone e valor.  
6. Frontend higieniza o telefone (apenas números) e codifica a mensagem URI.  
7. Frontend abre nova aba direcionando para o serviço `wa.me/55...`.  
8. Vendedor envia a mensagem e retorna o foco para a aba do sistema ERP.  
9. Frontend detecta o retorno de foco (`window.onfocus`) e dispara POST para registrar o contato.  
10. Backend inferi a autoria (Token JWT) e insere na tabela `orcamentos_contatos`.  
11. Frontend atualiza a linha na tabela visualmente com a tag "Contatado".  

**Exemplo Prático (Registro de Tracking):**
*Request:* `POST /orcamentos/df52d942-7bef-44a9-a8e8-f38127ecd6cc/contato` (Headers: Authorization Bearer)
*Response (200 OK):*
```json
{
  "mensagem": "Contato registrado com sucesso via WhatsApp",
  "orcamento_id": "df52d942-7bef-44a9-a8e8-f38127ecd6cc",
  "contatado": true,
  "vendedor_id": "11111111-1111-1111-1111-111111111111"
}

```

**Pós-condições (Sucesso):**

* Registro único (Append-Only) inserido em `orcamentos_contatos`.
* Orçamento filtrado para fora da visão de "Pendentes".

**Pós-condições (Falha):**

* Bloqueio da navegação e não abertura do link URI (Erro de front-end tratado).
* Nenhuma inserção ou mutação no banco de dados na ocorrência de HTTP 409 Conflict.

**Fluxos Alternativos**

* **A1: Cliente sem Telefone:** O sistema detecta a ausência. Fluxo abortado no navegador. Exibe alerta: "Cliente não possui telefone cadastrado."
* **A2: Orçamento já convertido (IDOR Preventivo):** Backend verifica o status do orçamento. Se FINALIZADA, retorna 409 Conflict. Ação de tracking rejeitada pelo backend.
* **A3: Duplo Clique de Janela:** A constraint UNIQUE da tabela protege o registro. Se o frontend disparar dois POSTs idênticos seguidos no retorno de foco, o cache estrutural absorve a chamada duplicada protegendo o banco contra falhas.

**Regras de Negócio (RN)**

* **RN-01:** O registro de contato só é aceito se o orçamento possuir status PENDENTE.
* **RN-02:** O número exportado para o `wa.me` deve obrigatoriamente possuir o DDI 55 inserido pelo frontend.
* **RN-03:** A autoria do log de contato é inferida do Token HTTP. O payload não trafega `user_id`.
* **RN-04:** Registros de contato são imutáveis (Append-Only Data). Não há rotas de UPDATE (PUT) ou DELETE para o rastreio comercial, a fim de garantir a irrefutabilidade das ações de auditoria.

**Requisitos Não-Funcionais (RNF)**

* **RNF-01:** O link para o WhatsApp deve abrir utilizando `target="_blank"`.
* **RNF-02:** A consulta de orçamentos (`JOIN` em código Python) não deve transpor 800ms de latência.
* **RNF-03:** É obrigatório o uso de `encodeURIComponent` no JS para blindagem XSS de URI.

---

## 4. PROTÓTIPO FUNCIONAL E INTEGRAÇÃO DE API

> **AVISO DE SEGURANÇA E PROTEÇÃO GLOBAL DE ROTAS (A01:2021)**
> Faz-se necessário explicitar que **absolutamente todas as rotas do backend** são protegidas pelo motor de identidade (UUID Session). Uma simples requisição direta via curl resultará em bloqueio (`401 Unauthorized` ou `403 Forbidden`). **Isto reflete a excelência do bloqueio global.** As evidências de by-pass estão descritas no documento-base RF-001.

**Operações Implementadas (CRUD Imutável de Contatos):**
Conforme delimitado pela **Regra de Negócio RN-04**, o log de auditoria comercial não provê operações de mutação (UPDATE) ou destruição (DELETE), protegendo a base de dados contra adulteração de relatórios.

| Operação | Método | Endpoint | Status Esperado |
| --- | --- | --- | --- |
| Create | POST | /orcamentos/{id}/contato (ou /contatar) | 200 OK / 201 Created |
| Read | GET | /orcamentos/pendentes-contato | 200 OK |

**Documentação Obrigatória da API:**
O OpenAPI oficializado da aplicação (Adequado ao padrão 3.0.x exigido na v16.3, detalhando parâmetros e os códigos de erro 401, 404 e 409 mapeados) está consolidado na raiz:
`docs/api/swagger.json`

---

## 5. ARQUITETURA E DECISÕES

### Diagrama de Arquitetura e Fluxo de Dados

```text
[ VENDEDOR (UI) ]
   │
   ▼ (1. Interage com Interface Web e Retorna Foco)
┌────────────────────────────────────────┐
│     Frontend (Vanilla JS / HTML)       │
│  - Higieniza Regex de Telefone         │
│  - Codifica XSS Payload via URI Encod. │
└───────────────────┬────────────────────┘
                    │ (2. Dispara API) POST /orcamentos/{id}/contato
                    ▼
┌────────────────────────────────────────┐
│       Backend API (FastAPI)            │
│  - Depends(get_current_user)           │
│  - Confirmação de Orçamento Pendente   │
└───────────────────┬────────────────────┘
                    │ (3. Insert)
                    ▼
┌────────────────────────────────────────┐
│   PostgreSQL / Supabase (Database)     │
│  - Tabela: orcamentos_contatos         │
│  - Constraints: UNIQUE e Cascades      │
└────────────────────────────────────────┘

```

**Fluxo de Dados:** `Vendedor -> Frontend (Event Listener) -> API Backend (Injeção AuthZ) -> PostgreSQL`.

### Decisões Técnicas (ADRs)

**ADR-031: Supressão Intencional de UPDATE e DELETE em Logs de Rastreio**

* **Razão:** O mapeamento de orçamentos contatados atua como uma trilha de auditoria comercial (*Audit Trail*). Se houvesse implementação das operações PUT e DELETE na API, um Vendedor ou Gestor poderia fraudar métricas apagando ou modificando o tracking.
* **Consequências:** A tabela obedece ao padrão *Append-Only*, limitando a arquitetura às operações CREATE e READ, maximizando a irrefutabilidade dos dados comerciais (Não-Repúdio).

**ADR-032: Controle de Acesso Baseado no Backend (Sem RLS no Supabase)**

* **Razão:** O DDL do banco de dados opera com *GRANT ALL* de forma intencional para identidades autenticadas. Optou-se por não engessar o banco com Row Level Security (RLS) complexas porque **100% da barreira AuthZ foi centralizada no FastAPI**. A injeção `Depends(RequireRole)` no Python atua como o porteiro absoluto (API Gateway) da aplicação.
* **Consequências:** Agilidade no desenvolvimento e controle fino de permissões feito na linguagem de programação principal da equipe, sem duplicar regras de negócio no banco.

---

## 6. SEGURANÇA OWASP

**1. Controle de Acesso (Broken Access Control - IDOR) - A01:2021**

* **Vulnerabilidade:** Um operador poderia forçar o POST de contato em um ID de orçamento finalizado para manipular dados (IDOR vertical/estado).
* **Implementação:** O Service realiza validação de estado. Se a resposta da base não for estritamente "PENDENTE", a operação é abortada (HTTP 409 Conflict).
* **Teste:** POST forçado via CURL contra um ID de orçamento já finalizado. Retorno da API bloqueia a gravação com código HTTP 409 ("Operação inválida: orçamento já convertido em venda").

**2. Insecure Design (Falsificação de Autoria) - A04:2021**

* **Vulnerabilidade:** O frontend poderia enviar o `user_id` no JSON, permitindo que um usuário imputasse sua ação a um colega.
* **Implementação:** A rota de criação desconsidera IDs via payload. A identidade do vendedor é extraída estritamente da decodificação criptográfica do Token HTTP.
* **Teste:** Envio manual via Postman de `{ "vendedor_id": "uuid-falso" }`. O sistema descarta a entrada (validação Pydantic extrínseca) e salva a auditoria usando o UUID real do Token assinante.

**3. Injection (Cross-Site Scripting / XSS no Deep Link) - A03:2021**

* **Vulnerabilidade:** Dados brutos do banco (nomes customizados com `<script>`) injetados diretamente na URL do WhatsApp ativariam falhas XSS baseadas em reflexão no navegador do usuário no momento do clique.
* **Implementação:** O envio de variáveis é higienizado pela função nativa `encodeURIComponent()` no Javascript, codificando caracteres especiais para formato hexadecimal seguro para URI.
* **Teste:** Nome de cliente modificado no banco para `Teste <script>alert(1)</script>`. O botão processou o clique transcrevendo a string para `%3Cscript%3E`, invalidando o código e forçando seu tratamento como texto inofensivo.
