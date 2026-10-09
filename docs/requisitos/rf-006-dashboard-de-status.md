# DOCUMENTO DE ESPECIFICAÇÃO DE REQUISITOS E ARQUITETURA SEGURA (SSD)

Laboratório de Inovação III — Prof. Edilberto Silva — 2026
VERSÃO 15.0 — COM VALIDAÇÃO AGNÓSTICA DE LINGUAGEM

## 1. METADADOS DO PROJETO E DA EQUIPE

### 1.1 Composição da Equipe

| ID | Nome Completo | Papel Primário | Papel Secundário | E-mail / Contato |
|:---:|:---|:---|:---|:---|
| 1 | João Pedro de Lima | Product Owner | Tech Lead / DevOps | joao52517876@edu.df.senac.br |
| 2 | Miguel Nunes | Desenvolvedor Back-End | Full Stack | miguel59970766@edu.df.senac.br |
| 3 | Luciano Santos | Desenvolvedor Back-End | Full Stack  | luciano58995256@edu.df.senac.br |
| 4 | Daniel Silva | DBA / Banco de Dados | Full Stack  | daniel52370026@edu.df.senac.br |
| 5 | Arthur Andrade | Desenvolvedor Front-End | Full Stack  | arthur59275206@edu.df.senac.br |
| 6 | Pedro Soares| Desenvolvedor Front-End | Full Stack  | pedro59153296@edu.df.senac.br |
| 7 | Matheus Chagas | AppSec / QA | Full Stack | matheus57119256@edu.df.senac.br |

### 1.2 Identificação

- **NOME_DO_PROJETO:** Sistema ERP - Loja de Construção
- **DESCRICAO_BREVE:** Sistema B2B de gestão, controle de orçamentos e auditoria de vendas voltado para gestores e vendedores de lojas de materiais de construção.

### 1.3 Localização dos Artefatos

- **LINK_REPOSITORIO_GITHUB:** [https://github.com/Jotajhones/sistema_ERP_LI3_FACSENAC](https://github.com/Jotajhones/sistema_ERP_LI3_FACSENAC)
- **BRANCH_PRINCIPAL:** main
- **LINK_APLICACAO_DEPLOY:** [https://sistema-erp-li3-facsenac.onrender.com/](https://sistema-erp-li3-facsenac.onrender.com/)
- **LINK_BANCO_DADOS:** [https://qlfjdnljfmicjkrbrwih.supabase.co/rest/v1/](https://qlfjdnljfmicjkrbrwih.supabase.co/rest/v1/)
- **LINK_API_SWAGGER:** [https://sistema-erp-li3-facsenac.onrender.com/docs](https://sistema-erp-li3-facsenac.onrender.com/docs)
- **LINK_DEMONSTRAÇÃO:** [https://sistema-erp-li-3-facsenac.vercel.app/](https://sistema-erp-li-3-facsenac.vercel.app/)

---

## RF-006: DASHBOARD DE STATUS E CONVERSÃO

### 1. IDENTIFICAÇÃO DO REQUISITO

**ID:** RF-006
**Título:** Dashboard de Status e Conversão de Orçamentos
**Tipo:** Requisito Funcional
**Prioridade:** ALTA
**Complexidade:** MÉDIA (estimado 5 story points)
**Status:** CONCLUÍDO
**Data de Criação:** 09/10/2026
**Última Atualização:** 09/10/2026

**Breve Descrição:**
O sistema deve prover um painel gerencial (dashboard) restrito, exibindo métricas legíveis sobre o status dos orçamentos, calculando automaticamente a taxa de conversão em ordens de serviço (vendas efetivadas), total orçado e pendente dentro de um período filtrado, facilitando a tomada de decisões da gestão.

---

### 2. DESCRIÇÃO E ATORES

**Descrição Detalhada:**
Por que este requisito existe?
O sistema precisa processar dados massivos de orçamentos e vendas para:

1. Apresentar métricas legíveis e táticas sobre a performance de vendas da loja.
2. Identificar gargalos na conversão de clientes (quantos orçamentos não viram vendas).
3. Auxiliar o gestor na tomada de decisões comerciais baseadas em dados financeiros (valor orçado vs valor efetivamente convertido).

**Atores do Sistema:**

1. **GESTOR / ADMIN (Ator Principal)**
Papel: Analisar a performance comercial.
Responsabilidade: Definir períodos de busca e analisar os dados gerados.
Permissões:
[X] READ (Acesso exclusivo para visualização dos indicadores gerenciais).
[ ] CREATE / UPDATE / DELETE (Não aplicável nesta tela específica).
2. **VENDEDOR (Ator Secundário Restrito)**
Papel: Operador de caixa.
Responsabilidade: Nenhuma nesta funcionalidade.
Permissões: Nenhuma (Acesso ao dashboard e suas rotas estritamente bloqueado).
3. **SISTEMA (Ator Automático)**
Papel: Motor analítico.
Responsabilidade: Proteger a rota, calcular índices complexos via RPC (Remote Procedure Call) no banco de dados, aplicar limites de 30 dias por padrão para evitar quebras, e formatar saídas monetárias.
Permissões: Acesso global de leitura no PostgreSQL via `service_role`.

---

### 3. ESPECIFICAÇÃO DE CASOS DE USO E REQUISITOS NÃO-FUNCIONAIS

**Caso de Uso (UC-006): Visualizar Dashboard de Conversão**

**Pré-Condições**

1. O usuário deve estar autenticado com um token válido e possuir perfil de GESTOR ou ADMIN.
2. A função `rf006_conversao_orcamentos` deve estar criada e com permissões corretas no Supabase.
3. Orçamentos devem existir no banco com os status correspondentes.

**Pós-Condições (Sucesso)**

1. Dados calculados, como taxa percentual de conversão e somatório de valores, exibidos na interface.
2. Experiência de usuário fluida, com o período dos últimos 30 dias carregado automaticamente.

**Pós-Condições (Falha)**

1. Exibição de alertas de interface em caso de datas vazias ou invertidas.
2. Bloqueio de acesso 403 retornado pela API para usuários não autorizados.
3. Exibição de erro amigável se a comunicação com o banco falhar (Erro 500).



**Fluxo Principal**

1. O Gestor acessa a interface de Dashboard.
2. O Sistema (Frontend) calcula as datas padrão (hoje e 30 dias atrás) e preenche os campos automaticamente.
3. O Sistema (Frontend) exibe estado de "Loading" e bloqueia o botão de filtro.
4. O Sistema (Frontend) envia requisição GET para `/dashboard/conversao-orcamentos` anexando os parâmetros de data e o Bearer Token.
5. O Sistema (Backend) valida a autorização (`RequireRole`) e os parâmetros de data.
6. O Sistema (Backend) repassa as datas inclusivas para a função RPC no Supabase, adicionando 1 dia à data final para fechamento exclusivo do banco.
7. O Banco de Dados executa o filtro processando o fuso horário `America/Sao_Paulo`.
8. O Banco de Dados calcula a taxa de conversão ignorando divisões por zero.
9. O Sistema (Backend) intercepta o JSON do banco, garante as tipagens de ponto flutuante e retorna status 200 OK.
10. O Sistema (Frontend) converte os dados para formato de moeda (BRL) e porcentagem, renderizando-os nos painéis numéricos.

**Fluxo Alternativo A1: Erro de Validação de Filtro de Data (Prevenção de Quebra)**
2a.1. O Gestor limpa os campos de data e clica em Aplicar Filtro.
2a.2. A função JavaScript `validarPeriodo` detecta a ausência de dados.
2a.3. O Frontend impede a requisição (que causaria Erro 422 na API) e exibe alerta: "Por favor, selecione as datas de início e fim."
2a.4. O fluxo é abortado até a correção do Gestor.

**Fluxo Alternativo A2: Tentativa de Acesso por Operador Comum (IDOR/Privilégio)**
4a.1. Um Vendedor descobre a URL da API e dispara requisição manual no Postman.
4a.2. O Middleware de segurança do Backend (`Depends(require_role(["ADMIN", "GESTOR"]))`) intercepta o token.
4a.3. A requisição é barrada imediatamente.
4a.4. A API retorna erro HTTP 403 Forbidden.

**Fluxo Alternativo A3: Falha de Permissão no Supabase (Erro 500)**
7a.1. O Backend tenta acionar a função RPC no banco.
7a.2. O banco retorna erro `42501 permission denied for function rf006_conversao_orcamentos`.
7a.3. O Backend intercepta a falha, envia o detalhe técnico real apenas para os logs do servidor, e lança uma `HTTPException` 500.
7a.4. O Frontend recebe o código 500, oculta o Loading e exibe tela de "Ocorreu um erro ao consultar os dados".

**Regras de Negócio (RN)**

| ID | Regra | Descrição |
| --- | --- | --- |
| **RN-01** | Controle de Visualização | Apenas administradores e gestores podem consumir os dados do painel gerencial.

 |
| **RN-02** | Período Padrão 30 Dias | A interface deve carregar nativamente com o filtro aplicado aos últimos 30 dias para evitar listagens massivas ou erros 422 por falta de parâmetros.

 |
| **RN-03** | Fuso Horário Comercial | O agrupamento dos dados no banco considera obrigatoriamente `AT TIME ZONE 'America/Sao_Paulo'`, desconsiderando o UTC dos servidores gringos.

 |
| **RN-04** | Exclusividade no Banco | O Backend envia a `data_fim` com acréscimo de 1 dia (+24h) para que o SQL faça o corte `< data_fim_exclusiva`, garantindo que eventos ocorridos às 23:59 entrem na conta.

 |
| **RN-05** | Divisão por Zero | O cálculo da taxa de conversão usa a função `NULLIF(count(*), 0)` no SQL para prevenir que a query falhe em meses sem nenhum orçamento gerado.

 |
| **RN-06** | Blindagem de Logs | Retornos 4xx ou 5xx nativos do Supabase (PostgREST) não podem trafegar até o cliente web, sendo mascarados por erros internos tratados na camada Service.

 |

**Requisitos Não-Funcionais (RNF)**

| ID | Atributo | Requisito | Justificativa |
| --- | --- | --- | --- |
| **RNF-01** | Performance | Índices SQL Composto | Necessário criar índice combinando `created_at` e `status` para acelerar o agrupamento de milhões de registros.

 |
| **RNF-02** | Desacoplamento | Modularização via RPC | O cálculo analítico deve rodar do lado do banco de dados (C/Postgres) ao invés da API (Python) para poupar uso de CPU no backend. |
| **RNF-03** | Tolerância a Falhas | Fail-safe visual | A página HTML deve possuir containeres `<section>` ocultos para os estados: loading, error, forbidden e empty, gerando resposta visual sem recarregar a tela.

 |

---

### 4. PROTÓTIPO FUNCIONAL 

**Estrutura de Arquivos:**

```text
src/rf-006-dashboard-de-status/
├── frontend/
│   └── dashboard/
│       ├── dashboard.css
│       ├── dashboard.html
│       └── services/
│           ├── app.js
│           └── dashboard.js
├── backend/
│   ├── routers/dashboard_router.py
│   ├── services/dashboard_service.py
│   ├── repositories/dashboard_repository.py
│   └── schemas/dashboard_schemas.py

```

**Arquivo HTML Base (frontend/dashboard/dashboard.html):**

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - ERP</title>
    <!-- Imports Padronizados e Corrigidos -->
    <link rel="stylesheet" href="../../rf-002-catalogo-produtos/frontend/styles/global.css">
    <link rel="stylesheet" href="../../rf-002-catalogo-produtos/frontend/header/header.css">
    <link rel="stylesheet" href="./dashboard.css">
</head>
<body>
    <div id="app-header"></div>
    <main class="erp-container">
        <section class="dashboard-filters">
            <div class="filter-group">
                <label for="dataInicio">Data início</label>
                <input type="date" id="dataInicio" class="erp-input">
            </div>
            <div class="filter-group">
                <label for="dataFim">Data fim</label>
                <input type="date" id="dataFim" class="erp-input">
            </div>
            <button type="button" id="btnAplicarFiltro" class="btn-primary">Aplicar</button>
        </section>

        <!-- Containeres de Estado -->
        <section id="dashboardLoading" class="dashboard-state" hidden><p>Carregando dados...</p></section>
        <section id="dashboardError" class="dashboard-state dashboard-state-error" hidden><h2 id="dashboardErrorText"></h2></section>
        
        <!-- Conteúdo Renderizado -->
        <section id="dashboardContent">
            <article class="conversion-card">
                <strong id="taxaConversao">0,00%</strong>
            </article>
            <!-- Outros cards de valor orçado, convertido e quantidades... -->
        </section>
    </main>
    <script src="../../rf-002-catalogo-produtos/frontend/scripts/env.js"></script>
    <script type="module" src="./services/app.js"></script>
</body>
</html>

```

**Script DDL (database/ddl/rf-006-conversao-orcamentos.sql):**

```sql
CREATE INDEX IF NOT EXISTS idx_orcamentos_periodo_status
    ON public.orcamentos (created_at)
    INCLUDE (status, valor_total);

CREATE OR REPLACE FUNCTION public.rf006_conversao_orcamentos(
    p_data_inicio date DEFAULT NULL,
    p_data_fim    date DEFAULT NULL
)
RETURNS json LANGUAGE sql STABLE SECURITY DEFINER SET search_path = public AS $$
    WITH base AS (
        SELECT o.status, o.valor_total
        FROM public.orcamentos o
        WHERE (p_data_inicio IS NULL OR o.created_at >= (p_data_inicio::timestamp AT TIME ZONE 'America/Sao_Paulo'))
          AND (p_data_fim IS NULL OR o.created_at < ((p_data_fim + 1)::timestamp AT TIME ZONE 'America/Sao_Paulo'))
    )
    SELECT json_build_object(
        'total_orcamentos', count(*),
        'convertidos', count(*) FILTER (WHERE status = 'CONVERTIDO'),
        'taxa_conversao', COALESCE(round(100.0 * count(*) FILTER (WHERE status = 'CONVERTIDO') / NULLIF(count(*), 0), 2), 0),
        'valor_total_orcado', COALESCE(sum(valor_total), 0)
    ) FROM base;
$$;

REVOKE ALL ON FUNCTION public.rf006_conversao_orcamentos(date, date) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.rf006_conversao_orcamentos(date, date) TO service_role;

```

---

### 5. ARQUITETURA E ADR (15%)

**Diagrama de Componentes**

```text
┌────────────────────────────────────────┐
│     Frontend (Vanilla JS / HTML)       │
│  - Calcula datas padrão (-30 dias)     │
│  - Bloqueia envio de campos nulos      │
└───────────────────┬────────────────────┘
                    │ GET /dashboard/conversao-orcamentos
                    ▼
┌────────────────────────────────────────┐
│       Backend API (FastAPI)            │
│  - require_role(["ADMIN", "GESTOR"])   │
│  - Adiciona +1 dia (data_fim_exclusiva)│
└───────────────────┬────────────────────┘
                    │ POST /rest/v1/rpc/rf006_conversao_orcamentos
                    ▼
┌────────────────────────────────────────┐
│   PostgreSQL / Supabase (RPC Call)     │
│  - Calcula fuso horário local          │
│  - Retorna métricas agregadas via JSON │
└────────────────────────────────────────┘

```

**ADR-020: Delegação de Processamento Analítico para RPC (Supabase)**

* **Status:** ACEITO
* **Contexto:** Consultar todos os orçamentos e baixar centenas de linhas de JSON para o Python realizar um laço `for` e calcular métricas esgotaria a memória RAM do servidor backend.
* **Decisão:** A lógica de sumarização (`COUNT`, `SUM`, `FILTER`) foi implementada diretamente no banco de dados via Stored Procedure (RPC) escrita em SQL estático, retornando apenas um bloco minúsculo de JSON consolidado para a API Python.


* **Consequências:** Alta escalabilidade, uso nulo de memória da aplicação, tráfego de rede ínfimo.

**ADR-021: Visualização Restrita baseada em Role**

* **Status:** ACEITO
* **Contexto:** Dados financeiros estratégicos não devem ser visíveis para todos os operadores da base.
* **Decisão:** Injeção do módulo de dependência RBAC nativo na rota FastAPI (`Depends(require_role(["ADMIN", "GESTOR"]))`), barrando liminarmente qualquer outro nível.


* **Consequências:** Vendedores não possuem autorização sequer para ler a rota na documentação.

**ADR-022: Padrão Dinâmico de 30 Dias na Interface**

* **Status:** ACEITO
* **Contexto:** A requisição sem parâmetros para a API disparava automaticamente o Erro 422 de processamento semantico do Pydantic, causando uma tela vermelha no primeiro carregamento do Dashboard.
* **Decisão:** Codificação de um script em Vanilla JS (função `definirDatasPadrao`) que calcula a data atual subtraindo 30 dias e insere esse intervalo nos parâmetros do payload de montagem da tela antes da primeira requisição disparar.
* **Consequências:** Prevenção total de quebras de aplicação ao iniciar e UX aprimorada.

**ADR-023: Fixação de Fuso Horário no Banco de Dados**

* **Status:** ACEITO
* **Contexto:** Como o Supabase salva a coluna `created_at` em formato global (UTC+0), buscas feitas no fim do dia (Brasil) cairiam no "dia seguinte" da query, adulterando indicadores de vendas diárias.
* **Decisão:** Fixação explícita da conversão transacional para `AT TIME ZONE 'America/Sao_Paulo'` dentro da função SQL RPC.


* **Consequências:** Resposta fiel ao turno comercial brasileiro independente do servidor estar localizado no leste americano.

**Tecnologias Escolhidas**

| Camada | Tecnologia | Justificativa |
| --- | --- | --- |
| Frontend | Vanilla JS (ES6+) | Não engessar a equipe com bibliotecas compiladas, focando em requisições Fetch diretas. |
| Backend | Python FastAPI | Desempenho concorrente, formatação de payloads tipados via Pydantic (`Schemas`). |
| Banco | Postgres (Supabase) | Funções RPC robustas para processamento semântico de Data/Hora (Timezone Analytics). |

---

### 6. VALIDAÇÃO DE SEGURANÇA OWASP 

**1. A01:2021 – Broken Access Control (Insecure API Endpoints)**

* **Vulnerabilidade:** Se um endpoint sensível for publicado no backend sem camadas de autorização acopladas, qualquer usuário autenticado conseguiria visualizar fluxos de caixa e performance empresarial burlando o frontend.
* **Implementação:** A rota de conversão no backend foi envolvida pela injeção `require_role`. Além disso, a função RPC no banco sofreu revogação completa de direitos (`REVOKE ALL FROM PUBLIC`), cedendo permissão exclusiva à identidade de serviço (`service_role`).


* **Teste:** Tentativa de acesso via token de VENDEDOR.

```bash
curl -X GET "http://127.0.0.1:8000/dashboard/conversao-orcamentos?data_inicio=2026-09-01&data_fim=2026-10-09" \
     -H "Authorization: Bearer [TOKEN_VENDEDOR]"

```

(Status 403 Forbidden retornado, assegurando a blindagem na camada do servidor, conforme executado no script `testes_curl.sh`).

**2. A03:2021 – Injection (Stored Procedure Injection)**

* **Vulnerabilidade:** A montagem de *queries* SQL através da interpolação de strings poderia permitir injeções maliciosas enviadas pelas datas no formulário frontend.
* **Implementação:** O uso de Stored Procedures RPC elimina as strings brutas do backend. A API FastAPI injeta rigorosamente um JSON estruturado cujos campos obedecem à tipagem restrita do banco (`p_data_inicio date`). A formatação da data do tipo string (YYYY-MM-DD) é verificada pelo `Pydantic` nativo do Python antes de trafegar na rede.


* **Teste:** Tentativa de injeção sintática via query parameter (`?data_inicio=2026-09-01'; DROP TABLE orcamentos;--`). A API detectou a string que não atende ao padrão ISO de calendário, abortando o parse e retornando Erro 422 Unprocessable Entity, poupando a requisição ao PostgreSQL.

**3. A05:2021 – Security Misconfiguration (Vazamento de Log Excepcional)**

* **Vulnerabilidade:** Se uma falha estrutural de permissão ocorresse (Ex: `permission denied for function`), o *stacktrace* gerado pelo PostgREST do Supabase poderia ser devolvido ao usuário final, revelando a tabela ou nome das funções de arquitetura do banco.


* **Implementação:** No módulo `dashboard_repository.py`, as chamadas REST estão encapsuladas em um bloco `Try/Except`. O corpo da resposta mal-sucedida do banco (`response.text`) foi isolado em logs silenciosos (`logger.error()`), e a exceção genérica limpa `DashboardErroInternoError` foi repassada até o Frontend.


* **Teste:** Simulação forçada de desautorização do RPC.
*(O terminal do servidor acusa: `Supabase respondeu 401: {"code":"42501","message":"permission denied for function rf006_conversao_orcamentos"}`. Contudo, o cliente API/Web recebe apenas um 500 simplificado: "Erro interno ao calcular a conversão de orçamentos", mascarando a topologia interna do banco)*.

