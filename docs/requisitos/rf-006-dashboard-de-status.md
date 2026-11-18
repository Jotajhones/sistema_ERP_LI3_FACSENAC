# DOCUMENTO DE ESPECIFICAÇÃO DE REQUISITOS E ARQUITETURA SEGURA (SSD)

Laboratório de Inovação III — Prof. Edilberto Silva — 2026
VERSÃO 16.3 — COM VALIDAÇÃO AGNÓSTICA DE LINGUAGEM

## 1. METADADOS DO PROJETO E DA EQUIPE

### 1.1 Identificação

- **ID:** RF-006  
- **Título:** Dashboard de Status e Conversão de Orçamentos  
- **Tipo:** Requisito Funcional  
- **Prioridade:** ALTA  
- **Complexidade:** MÉDIA (estimado 5 story points)  
- **Status:** CONCLUÍDO  

### 1.2 Localização dos Artefatos (URLs Obrigatórias)

- **a) URL da Aplicação (Deploy Online):** https://sistema-erp-li-3-facsenac.vercel.app/ (Frontend Hospedado na Vercel)
- **b) Link do Banco de Dados Online:** https://supabase.com/dashboard/project/qlfjdnljfmicjkrbrwih/editor/ (Leitura para prof.edilberto.silva@gmail.com)
- **c) Link do GitHub (Repositório):** https://github.com/Jotajhones/sistema_ERP_LI3_FACSENAC (Branch: main)

*(Nota de Infraestrutura: A API Backend opera sob o domínio https://sistema-erp-li3-facsenac.onrender.com. O tempo de resposta inicial pode sofrer atraso de até 50 segundos devido ao "Cold Start" dos contêineres gratuitos do Render.com).*

### 1.3 Composição da Equipe

| ID | Nome Completo | Papel Primário | Papel Secundário | E-mail / Contato |
|:---:|:---|:---|:---|:---|
| 1 | João Pedro de Lima | Product Owner | Tech Lead / DevOps | joao52517876@edu.df.senac.br |
| 2 | Miguel Nunes | Desenvolvedor Back-End | Full Stack | miguel59970766@edu.df.senac.br |
| 3 | Luciano Santos | Desenvolvedor Back-End | Full Stack  | luciano58995256@edu.df.senac.br |
| 4 | Daniel Silva | DBA / Banco de Dados | Full Stack  | daniel52370026@edu.df.senac.br |
| 5 | Arthur Andrade | Desenvolvedor Front-End | Full Stack  | arthur59275206@edu.df.senac.br |
| 6 | Pedro Soares| Desenvolvedor Front-End | Full Stack  | pedro59153296@edu.df.senac.br |
| 7 | Matheus Chagas | AppSec / QA | Full Stack | matheus57119256@edu.df.senac.br |

---

## 2. DESCRIÇÃO E ATORES

**Descrição Detalhada:**
O RF-006 implementa o painel analítico gerencial (Dashboard) do sistema ERP. Ele tem como propósito transformar os dados operacionais brutos de geração de orçamentos e conversão em Ordens de Serviço (vendas) em inteligência de negócio acionável.

Através do painel, a gerência da loja de materiais de construção consegue monitorar o fluxo de caixa presumido (total orçado) e o fluxo de caixa efetivado (total convertido), identificando a eficiência da equipe de vendas em determinados recortes de tempo.

A funcionalidade consolida os dados na camada do banco de dados (via RPC) para garantir alta performance, protegendo as informações táticas da empresa através de um controle de acesso rigoroso que bloqueia a visualização por operadores de base.

**Benefícios para o Negócio:**
1. Apresentar métricas legíveis e táticas sobre a performance de vendas da loja.
2. Identificar gargalos na conversão de clientes (quantos orçamentos não viram vendas).
3. Auxiliar o gestor na tomada de decisões comerciais baseadas em dados financeiros (valor orçado vs valor efetivamente convertido).

**Atores do Sistema:**

1. **GESTOR / ADMIN (Ator Principal)**
- **Papel:** Analisar a performance comercial e definir períodos de busca.
- **Permissões:** READ (Acesso exclusivo para visualização dos indicadores gerenciais).

2. **VENDEDOR (Ator Secundário Restrito)**
- **Papel:** Operador de caixa.
- **Permissões:** Nenhuma. Acesso ao dashboard e suas rotas estritamente bloqueado.

3. **SISTEMA (Ator Automático)**
- **Papel:** Motor analítico e validador de tráfego.
- **Permissões:** Acesso global de leitura no PostgreSQL via `service_role` para execução de RPC.

---

## 3. ESPECIFICAÇÃO DE CASOS DE USO E REQUISITOS NÃO-FUNCIONAIS

**Caso de Uso (UC-006): Visualizar Dashboard de Conversão**

**Pré-Condições**
1. O usuário deve estar autenticado com um token válido e possuir perfil de GESTOR ou ADMIN.
2. A função `rf006_conversao_orcamentos` deve estar criada e com permissões corretas no Supabase.
3. Orçamentos devem existir no banco com os status correspondentes.

**Pós-Condições (Sucesso)**
1. Dados calculados exibidos na interface de forma modular e tipada (Moeda BRL e Porcentagem).

**Pós-Condições (Falha)**
1. Exibição de alertas de interface na ausência de filtros ou falha de comunicação (Erro 500 amigável).
2. Transações bloqueadas via HTTP 403 Forbidden para atores não autorizados (Vendedores).

**Fluxo Principal**
1. O Gestor acessa a interface de Dashboard.
2. O Sistema (Frontend) calcula as datas padrão (hoje e 30 dias atrás) e preenche os campos automaticamente.
3. O Sistema (Frontend) exibe estado de "Loading" e bloqueia o botão de filtro.
4. O Sistema (Frontend) envia requisição GET para `/dashboard/conversao-orcamentos` anexando os parâmetros de data e o Bearer Token.
5. O Sistema (Backend) valida a autorização (`RequireRole`) e os parâmetros de data.
6. O Sistema (Backend) repassa as datas para a função RPC no Supabase, adicionando 1 dia à data final.
7. O Banco de Dados executa o filtro processando o fuso horário `America/Sao_Paulo`.
8. O Banco de Dados calcula a taxa de conversão ignorando divisões por zero e retorna o JSON.
9. O Sistema (Backend) repassa a métrica. Retorna status 200 OK.
10. O Sistema (Frontend) converte os dados para BRL e renderiza.

**Exemplo Prático (Requisição e Resposta):**
*Request:* `GET /dashboard/conversao-orcamentos?data_inicio=2026-09-01&data_fim=2026-10-09`
*Response (200 OK):*
```json
{
  "total_orcamentos": 150,
  "convertidos": 45,
  "taxa_conversao": 30.00,
  "valor_total_orcado": 125000.50
}

```

**Fluxos Alternativos**

* **A1: Erro de Validação de Filtro de Data:** O Gestor limpa os campos de data e clica em Aplicar Filtro. O Frontend impede a requisição (que causaria Erro 422 na API) e exibe alerta: "Por favor, selecione as datas de início e fim."
* **A2: Tentativa de Acesso por Vendedor (IDOR):** Um Vendedor descobre a URL da API e dispara requisição manual. O Middleware `Depends(require_role(["ADMIN", "GESTOR"]))` intercepta e retorna erro HTTP 403 Forbidden.
* **A3: Falha de Permissão no BD:** O banco retorna erro de permissão na RPC. O Backend intercepta, loga internamente e lança `HTTPException` 500 mascarada. O Frontend exibe: "Ocorreu um erro ao consultar os dados".

**Regras de Negócio (RN)**

* **RN-01:** Apenas administradores e gestores podem consumir os dados do painel gerencial.
* **RN-02:** A interface deve carregar nativamente com o filtro aplicado aos últimos 30 dias.
* **RN-03:** O agrupamento dos dados no banco considera obrigatoriamente `AT TIME ZONE 'America/Sao_Paulo'`.
* **RN-04:** O Backend envia a `data_fim` com acréscimo de 1 dia (+24h) para o corte exclusivo do SQL.
* **RN-05:** O cálculo da taxa de conversão usa `NULLIF(count(*), 0)` no SQL para prevenir divisão por zero.
* **RN-06:** Retornos 4xx ou 5xx nativos do Supabase não trafegam até o cliente web, sendo mascarados na camada Service.

**Requisitos Não-Funcionais (RNF)**

* **RNF-01:** Índices SQL Composto (`created_at` e `status`) para acelerar o agrupamento de milhões de registros.
* **RNF-02:** Modularização via RPC no PostgreSQL para poupar uso de CPU e memória RAM no backend.
* **RNF-03:** A página HTML deve possuir containeres estáticos ocultos para loading e erro para respostas visuais imediatas.

---

## 4. PROTÓTIPO FUNCIONAL E INTEGRAÇÃO DE API

Interface operando ativamente em: https://sistema-erp-li-3-facsenac.vercel.app/

**Operações Implementadas:**

| Operação | Método | Endpoint | Status Esperado |
| --- | --- | --- | --- |
| Read | GET | /dashboard/conversao-orcamentos | 200 OK |

**Documentação Obrigatória da API:**
O arquivo técnico OpenAPI, padrão 3.0.x exigido pelo protocolo, encontra-se documentado e versionado na raiz do repositório em:
`docs/api/swagger.json`

---

## 5. ARQUITETURA E DECISÕES

### Diagrama de Arquitetura e Fluxo de Dados

```text
[ GESTOR ]
   │
   ▼ (1. Interage com Interface Web)
┌────────────────────────────────────────┐
│     Frontend (Vanilla JS / HTML)       │
│  - Calcula datas padrão (-30 dias)     │
│  - Bloqueia envio de campos nulos      │
└───────────────────┬────────────────────┘
                    │ (2. Dispara Request) GET /dashboard/conversao-orcamentos
                    ▼
┌────────────────────────────────────────┐
│       Backend API (FastAPI)            │
│  - require_role(["ADMIN", "GESTOR"])   │
│  - Adiciona +1 dia (data_fim_exclusiva)│
└───────────────────┬────────────────────┘
                    │ (3. RPC Execution) POST /rest/v1/rpc/...
                    ▼
┌────────────────────────────────────────┐
│   PostgreSQL / Supabase (Database)     │
│  - Calcula fuso horário local          │
│  - Agrupa SUM e COUNT nativamente      │
└───────────────────┬────────────────────┘
                    │ (4. Retorna JSON Consolidado)
                    ▼
[ GESTOR VISUALIZA MÉTRICAS ]

```

**Fluxo de Dados de Arquitetura:**
`Usuário (Gestor) -> Frontend (Vercel/JS) -> Backend (Render/FastAPI) -> Banco de Dados (Supabase/PostgreSQL)`.

### Decisões Técnicas (ADRs)

**ADR-020: Delegação de Processamento Analítico para RPC (Supabase)**

* **Razão:** Consultar todos os orçamentos e baixar centenas de linhas para o Python calcular métricas esgotaria a memória RAM do servidor gratuito. A lógica foi migrada via Stored Procedure (RPC) escrita em SQL.
* **Consequências:** Alta escalabilidade, uso nulo de memória da aplicação backend e tráfego de rede ínfimo.

**ADR-021: Cold-Start e Resiliência de Frontend**

* **Razão:** O Backend no serviço Render desliga os contêineres após inatividade.
* **Consequências:** O Frontend foi desenhado com estados de `Loading` independentes para suportar tranquilamente a espera de até 50 segundos da primeira requisição do dia sem quebrar a interface (Timeout Tolerance).

---

## 6. SEGURANÇA OWASP

**1. Controle de Acesso (Broken Access Control) - A01:2021**

* **Vulnerabilidade:** Se um endpoint sensível for publicado sem camadas de autorização acopladas, qualquer usuário visualizaria o fluxo de caixa empresarial.
* **Implementação:** A rota foi protegida por `Depends(require_role(["ADMIN", "GESTOR"]))`.
* **Teste:** Tentativa de acesso via curl com token de VENDEDOR resulta em status 403 Forbidden retornado pelo servidor, não alcançando o banco de dados.

**2. Injection (Stored Procedure Injection) - A03:2021**

* **Vulnerabilidade:** Montagem de *queries* SQL via strings permitiriam injeções maliciosas enviadas pelas datas.
* **Implementação:** O uso de Stored Procedures RPC elimina as strings brutas do backend. A formatação da data do tipo string (YYYY-MM-DD) é sanitizada pelo `Pydantic` nativo do Python antes de trafegar na rede.
* **Teste:** Requisição com query parameter `?data_inicio=2026-09-01'; DROP TABLE orcamentos;--`. A API Pydantic aborta o parse e retorna 422 Unprocessable Entity.

**3. Security Misconfiguration (Vazamento de Log Excepcional) - A05:2021**

* **Vulnerabilidade:** Em falhas de SGBD, o *stacktrace* do PostgREST poderia ser devolvido ao usuário final, revelando a tabela.
* **Implementação:** As chamadas REST estão encapsuladas em blocos `Try/Except`. O corpo da resposta do banco é isolado, devolvendo uma `HTTPException(500)` limpa ao frontend.
* **Teste:** Revogação de acesso da RPC no Supabase. A API Python capta o 401 do banco, oculta o payload técnico e emite o 500 amigável para o cliente.


