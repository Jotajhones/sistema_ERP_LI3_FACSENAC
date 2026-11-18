# DOCUMENTO DE ESPECIFICAÇÃO DE REQUISITOS E ARQUITETURA SEGURA (SSD)
Laboratório de Inovação III — Prof. Edilberto Silva — 2026
VERSÃO 16.3 — COM VALIDAÇÃO AGNÓSTICA DE LINGUAGEM

## 1. METADADOS DO PROJETO E DA EQUIPE

### 1.1 Identificação
NOME_DO_PROJETO: Sistema ERP Construção
DESCRICAO_BREVE: Documento consolidado atestando a integridade final do MVP v1.0.0, com foco na estabilidade arquitetural, correções de segurança apontadas em auditorias anteriores e fechamento do segundo bimestre.

### 1.2 Localização dos Artefatos (URLs Obrigatórias)
LINK_REPOSITORIO_GITHUB: https://github.com/Jotajhones/sistema_ERP_LI3_FACSENAC
LINK_APLICACAO_DEPLOY: https://sistema-erp-li-3-facsenac.vercel.app/
LINK_BANCO_DADOS: https://supabase.com/dashboard/project/qlfjdnljfmicjkrbrwih/editor/
LINK_DEMONSTRAÇÃO: https://sistema-erp-li-3-facsenac.vercel.app/

*(Nota Arquitetural: O front-end encontra-se hospedado na Vercel no link acima. A API RESTful de backend opera sob o domínio https://sistema-erp-li3-facsenac.onrender.com, consolidando o modelo Jamstack).*

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

# RF-009: Consolidação Final do Projeto

## 1. Identificação

- **ID:** RF-009
- **Título:** Entrega Final e Consolidação do Projeto
- **Prioridade:** Máxima
- **Complexidade:** 3 story points
- **Status:** CONCLUÍDO

### a) URL da Aplicação (Deploy Online)
- **URL:** https://sistema-erp-li-3-facsenac.vercel.app/
- **Plataforma:** Vercel
- **Acesso:** Público

### b) Link do Banco de Dados Online
- **BD:** Supabase (PostgreSQL)
- **Link:** https://supabase.com/dashboard/project/qlfjdnljfmicjkrbrwih/editor/
- **Acesso:** Leitura para o professor (email: prof.edilberto.silva@gmail.com)
- **Tabela principal:** Multi-table (Ref: users, produtos, orcamentos)

### c) Link do GitHub (Repositório)
- **Repositório:** https://github.com/Jotajhones/sistema_ERP_LI3_FACSENAC
- **Branch principal:** main
- **Estrutura:** Conforme guia (docs/, src/, database/)

---

## 2. Descrição e Atores

O RF-009 atua exclusivamente como o marco de entrega final e auditoria do MVP v1.0.0. Conforme acordado com a curadoria técnica (Professor Edilberto), não houve a geração de novo código funcional ou novas interfaces para este requisito, uma vez que o sistema já cumpre com excelência todos os requisitos estruturais previstos e avaliados.

Este documento consolida o sucesso das implementações do segundo bimestre, além de apresentar as justificativas técnicas finais que sanam apontamentos gerados por avaliações automatizadas (IA) nas etapas RF-006 e RF-007. O foco desta entrega é a estabilidade, a segurança e a aderência estrita à Governança (Guia v16.3).

### Benefícios para o Negócio
- Prevenção do *Feature Creep*: Garantia de um código limpo, estável e livre de funcionalidades descartáveis de última hora.
- Manutenção da coesão do MVP, blindando as operações da loja de materiais de construção em um ambiente testado e previsível.
- Centralização da responsabilidade de segurança na API (Server-Side), simplificando a gestão do banco de dados.

### Atores

#### Gestor / Admin
- **Papel:** Utilizador pleno do sistema consolidado.
- **Permissões:** Acesso total (CRUD) auditado por RBAC nas rotas do painel.
- **Acesso:** Todas as telas de operação e Dashboards.

#### Vendedor
- **Papel:** Operador de fluxo rápido no PDV.
- **Permissões:** Acesso isolado e restrito (Read/Create) ao domínio comercial.
- **Acesso:** Orçamentos, catálogo de produtos e painel pessoal.

#### Sistema (Automático)
- **Papel:** Provedor da base unificada e motor de validação.
- **Permissões:** Gestão de sessão por UUID, controle de triggers e RPCs analíticos.

---

## 3. Casos de Uso e Requisitos Não-Funcionais

### Fluxo Principal: Validação da Consolidação do MVP

**Pré-condições:**
- O avaliador acessa os artefatos nos diretórios previamente construídos (ex: `src/rf-006-dashboard-de-status/`, `src/rf-007-tracking-clientes/`, `src/rf-008-recuperar-senha/`).

**Fluxo:**
1. O Avaliador consulta o código das rotas e constata que estão isoladas e protegidas pelo middleware em FastAPI.
2. O Avaliador lê a documentação da API em `./docs/api/swagger.json` e atesta sua conformidade com a especificação técnica dos endpoints implementados.
3. O Avaliador constata as justificativas arquiteturais deste documento, que esclarecem as remoções de rotas inseguras (como PUT/DELETE em logs de auditoria).
4. O Avaliador acessa a aplicação na Vercel, certificando-se de que a comunicação com o backend (Render.com) opera fluidamente após o cold-start.

**Pós-condições:**
- Sistema formalmente aceito como "Estável e Funcional" em sua versão V1.0.0.
- Auditoria de segurança OWASP comprovada nas rotas consolidadas.

### Regras de Negócio Consolidadas

- **RN-01:** Congelamento de Código: Para preservar a integridade das notas já consolidadas, o repositório teve suas ramificações primárias unificadas, proibindo a inserção de novos recursos na Sprint Final.
- **RN-02:** Governança Ativa e Bloqueio Global: As restrições severas de API (ex: `Depends(RequireRole)`) atuam em 100% dos endpoints de mutação e consulta analítica desenvolvidos.
- **RN-03:** Imutabilidade de Auditoria: Os registros de tracking e log gerados pelo sistema (ex: `orcamentos_contatos`) são de acréscimo contínuo (append-only). É estritamente proibida a existência de rotas de exclusão (DELETE) ou atualização (PUT) para estes dados, preservando a rastreabilidade fiscal e comercial.

### Requisitos Não-Funcionais Consolidadas

- **RNF-01:** Resiliência Híbrida: O *frontend* está preparado para aguardar o *cold-start* intrínseco dos contêineres gratuitos do serviço Render.com, sem apresentar falhas fatais à experiência do usuário durante o aquecimento da API.

---

## 4. Protótipo Funcional e Integração de API

> **AVISO DE SEGURANÇA E PROTEÇÃO GLOBAL DE ROTAS (A01:2021)**
>
> Faz-se necessário explicitar novamente que **absolutamente todas as rotas do backend desta aplicação** são rigorosamente protegidas pelo motor de identidade consolidado no MVP (UUID de Sessão). 
>
> Uma requisição GET/POST direta aos endpoints via navegador ou ferramentas de teste (ex: Postman/Curl), sem o contexto de autenticação válido injetado nos headers, resultará em bloqueio liminar (`401 Unauthorized` ou `403 Forbidden`). **Isto reflete o sucesso da implementação de segurança, e não um defeito nas rotas da API.**

O acesso aos protótipos visuais consolidados referentes ao fechamento do projeto deve ser realizado nas interfaces já entregues e hospedadas na Vercel.

**Operações Auditáveis (Reflexo das Sprints 06-08):**
- **Dashboard (RF-006):** Métricas operadas em banco de dados via RPC seguro.
- **Tracking (RF-007):** Registro de atendimento a orçamentos abandonados.
- **Reset Administrativo (RF-008):** Resgate de contas por meio de reescrita criptográfica isolada de hash (bcrypt) e invalidação de sessão.

**Documentação Obrigatória da API:**
O arquivo técnico OpenAPI 3.0, consolidando as rotas mantidas ao longo do semestre e refletindo com exatidão os métodos disponíveis e os payloads exigidos, encontra-se atualizado em:
`docs/api/swagger.json`

---

## 5. Arquitetura e Decisões

### Componentes da Arquitetura
A arquitetura final do ERP atua em conformidade com os princípios RESTful e estruturação em microsserviços lógicos:
- **Frontend (Presentation):** HTML5, CSS3 e Vanilla JavaScript operando Fetch APIs.
- **Backend (Business Logic & AuthZ):** Python com FastAPI, isolando regras de negócio nos *Services* e definindo esquemas de dados estritos via *Pydantic*.
- **Data (Persistence & Analytics):** PostgreSQL gerenciado via Supabase.

### Decisões Técnicas de Consolidação (ADRs)

**ADR-030: Finalização do Projeto (Congelamento Sem Novo Artefato)**
- **Razão:** O projeto cumpre com excelência as requisições delimitadas do RF-006 ao RF-008. Iniciar um fluxo de código não alinhado ao *core business* do ERP apenas para cumprir tabela burocrática aumentaria a dívida técnica de forma injustificável.
- **Consequências:** A entrega do RF-009 constitui-se como o fechamento gerencial e blindagem documental do MVP.

**ADR-031: Supressão de Rotas de Modificação em Logs de Tracking (Resposta à Avaliação RF-007)**
- **Razão:** Em avaliações automatizadas anteriores, foi apontada a ausência das rotas `PUT` e `DELETE` na funcionalidade de tracking de contatos (RF-007). A equipe técnica optou conscientemente por não implementá-las. A tabela `orcamentos_contatos` funciona como um *Log de Auditoria* de ações comerciais. Implementar rotas de alteração (PUT) ou deleção (DELETE) sobre estes registros permitiria a falsificação do histórico de produtividade, ferindo o princípio do repúdio.
- **Consequências:** As operações para essa entidade limitam-se estritamente ao CREATE e READ, refletindo o modelo correto de segurança da informação (Append-Only Data).

**ADR-032: Centralização do Role-Based Access Control (RBAC) no Server-Side**
- **Razão:** Optou-se por não implementar lógicas complexas de Row Level Security (RLS) internamente nas configurações do Supabase. A decisão fundamenta-se no fato de que 100% da segurança e interceptação de rotas está centralizada na injeção de dependência do FastAPI (`Depends(RequireRole)`). O banco de dados só atende requisições caso a API autorize o tráfego, criando um gargalo de segurança centralizado e fácil de auditar no código Python.
- **Consequências:** Manutenção facilitada da camada de segurança na API e prevenção de duplicação de lógicas de negócio no SGBD.

---

## 6. Segurança OWASP (Revisão Consolidada)

As fundações de segurança estruturadas pela equipe permanecem intactas e blindam as operações da loja corporativa contra as principais vulnerabilidades catalogadas pela OWASP.

### Controle 1: Insecure Direct Object Reference (Broken Access Control) - A01:2021
**Implementação Consolidada:** Toda a arquitetura foi desenhada sobrepondo os privilégios do usuário. Endpoints de mutação não confiam em parâmetros como `user_id` originados do payload do Frontend (que poderiam ser facilmente adulterados no DevTools). O ID do responsável pela ação é sempre extraído da descriptografia do Token UUID, impedindo a falsificação ideológica e a escalada horizontal. Qualquer tentativa direta de burla ao sistema via rotas abertas é barrada por validadores que forçam a resposta `HTTP 403 Forbidden`.

### Controle 2: Cryptographic Failures - A02:2021
**Implementação Consolidada:** A manipulação de credenciais no RF-008 ocorre unicamente na memória do servidor backend. Não há transmissão de senhas em *plain-text* geradas sistemicamente através da rede. O banco de dados Supabase é povoado apenas com dados irreconhecíveis gerados através de hashes salteados pelo algoritmo *bcrypt* (Cost: 12), invalidando tentativas de engenharia reversa.

### Controle 3: Security Misconfiguration (Tratamento de Exceções) - A05:2021
**Implementação Consolidada:** Foi garantida a neutralidade dos erros devolvidos à interface. Em situações onde o SGBD PostgreSQL apresente falhas (como quebras de constraint ou permissões insuficientes ao rodar uma RPC), o backend FastAPI intercepta o *Traceback*, registra o erro real e devolve ao Frontend apenas códigos padronizados (ex: `HTTP 500`) acompanhados de mensagens genéricas. Isto evita o vazamento da topologia do banco de dados e de detalhes da estrutura de pastas do servidor para o usuário final.