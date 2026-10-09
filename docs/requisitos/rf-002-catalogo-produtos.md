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

## RF-002: CATÁLOGO DE PRODUTOS E GESTÃO DE SESSÕES

### 1. IDENTIFICAÇÃO DO REQUISITO

**ID:** RF-002
**Título:** Catálogo de Produtos e Sessões Restritas
**Tipo:** Requisito Funcional
**Prioridade:** ALTA (Habilita a futura criação de Ordens de Serviço e Orçamentos)
**Complexidade:** ALTA (estimado 8 story points)
**Status:** CONCLUÍDO (Refatorado na Sprint 05)
**Data de Criação:** 02/09/2026
**Última Atualização:** 09/10/2026

**Breve Descrição:**
Criar o catálogo de itens do ERP com operações integrais de CRUD (criação, leitura, atualização e deleção lógica). O módulo é protegido por um sistema de Sessões Opacas (UUID), onde a interface aplica controle de acesso baseado em papéis (RBAC), limitando as ações administrativas.

---

### 2. DESCRIÇÃO E ATORES

**Descrição Detalhada e Contexto do Negócio:**
Para que a loja fature, os vendedores consultam o catálogo para preparar orçamentos. Simultaneamente, gestores operam a manutenção dos preços e inserção de novos SKUs. Todo esse tráfego precisa ser assegurado por rotas blindadas, onde ações de mutação carimbam a autoria no banco.

**Objetivos de Negócio (Benefícios):**
1. Unificar 100% da precificação da loja, evitando orçamentos com valores desatualizados.
2. Garantir integridade de rastreabilidade (auditoria) marcando a coluna `criado_por` e `atualizado_por`.
3. Prevenir a corrupção do histórico de vendas aplicando Deleção Lógica em vez de física para produtos fora de linha.

**Atores do Sistema:**

1. **GESTOR / ADMIN (Ator Principal)**
Papel: Administrador do inventário da loja.
Permissões:
[X] CREATE (Cadastrar novos SKUs).
[X] READ (Listagem integral do estoque).
[X] UPDATE (Editar dados e atualização de preços).
[X] DELETE (Aplicar inativação lógica).

2. **VENDEDOR (Ator Secundário Restrito)**
Papel: Operador comercial.
Permissões:
[X] READ (Visualizar listagem pública e buscar termos).
[ ] CREATE / UPDATE / DELETE (Sem privilégios de mutação).

3. **SISTEMA (Ator Automático)**
Papel: Middleware validador de acesso.
Permissões: Ler e invalidar tokens de acesso diretamente na tabela `sessoes` do PostgreSQL.

---

### 3. ESPECIFICAÇÃO DE CASOS DE USO E REQUISITOS NÃO-FUNCIONAIS

**Caso de Uso (UC-002): Gerenciar e Consultar Catálogo**

**Pré-Condições**
1. O usuário possui um Token válido armazenado no navegador após o RF-001.
2. A API FastAPI está operacional e autenticando UUIDs via Middleware.

**Pós-Condições (Sucesso)**
1. A base de dados processa e persiste a inclusão ou alteração do produto.
2. O histórico de auditoria (`atualizado_por`) é preenchido com a identidade extraída do token.

**Pós-Condições (Falha)**
1. Acesso bloqueado com Erro HTTP 403 Forbidden para tentativas de alteração por Vendedores.

**Fluxo Principal (Criação e Consulta)**
1. O usuário acessa a página do Catálogo de Produtos.
2. O Frontend aciona script RBAC que avalia o perfil (`user_role`).
3. O Frontend esconde o botão "Novo Produto" caso a *role* seja VENDEDOR.
4. O Frontend dispara requisição `GET /produtos` com o cabeçalho Authorization Bearer.
5. O Backend localiza o token no banco de dados, confirmando a sessão.
6. O Backend lista os produtos com `ativo = true`.
7. O Frontend recebe e mapeia os itens numa tabela HTML.
8. Um Gestor clica em Editar e submete um formulário corrigindo o valor.
9. O Backend (rota `PUT /produtos/{id}`) valida o token, recalcula a auditoria e salva o novo preço.

**Fluxos Alternativos**
* **A1: Cadastro com Valor Negativo (Recusa):** No passo 8, o Gestor digita um valor menor que zero. A API aciona o Pydantic, que recusa o Payload com Erro HTTP 422 antes da submissão ao banco.
* **A2: Token Expirado/Inválido:** No passo 5, o backend não acha o UUID na tabela de sessões. O retorno é 401 Unauthorized. O frontend intercepta, destrói o localStorage e ejeta o usuário.
* **A3: Bypass de Formulário (Postman):** Um Vendedor abre o Postman e dispara um `PUT /produtos/123`. A dependência `RequireRole` do FastAPI barra o fluxo no primeiro ciclo, retornando erro 403.

**Regras de Negócio (RN)**

| ID | Regra | Descrição |
|---|---|---|
| RN-01 | Valor Positivo | Nenhum produto pode registrar `valor_venda` negativo (Constraint CHECK no Postgres). |
| RN-02 | Unicidade de Estoque | O código SKU deve ser estritamente único (UNIQUE). |
| RN-03 | Soft Delete Contábil | Produtos são inativados marcando `ativo = false`, proibindo-se exclusões com `DELETE` explícito. |
| RN-04 | Auditoria Mandatória | Toda ação de inserção (POST) ou edição (PUT) exige o carimbo obrigatório do UUID do requisitante logado. |

**Requisitos Não-Funcionais (RNF)**

| ID | Atributo | Requisito | Métrica | Justificativa |
|---|---|---|---|---|
| RNF-01 | Performance | Latência de Busca | Consultas textuais (`ilike`) devem retornar a listagem em < 800ms. | A agilidade da busca no PDV impacta o atendimento ao cliente. |
| RNF-02 | Usabilidade | Ocultação Condicional | Componentes proibidos não devem renderizar mensagens de erro na tela, apenas serem ocultos (display:none). | Menos ruído visual. |
| RNF-03 | Segurança | Isolamento de Sessão | Tokens Bearer expirados devem ser rejeitados ativamente pelo banco (Tabela `sessoes`). | Evitar spoofing. |

---

### 4. PROTÓTIPO FUNCIONAL E CÓDIGO (50%)

**Aviso de Evolução de Sprint (UPDATE e Interface Web):**
Durante a avaliação da Sprint 02, o backend das operações essenciais operava com 75% da sua plenitude. Conforme exigido pela avaliação de QA formal (Avaliador Claude/Prof. Edilberto), as rotas de `UPDATE` e o protótipo de frontend com formulários JS foram devidamente integrados, finalizados e estabilizados no fechamento da versão 1.0.0 (durante o escopo do RF-005).

**Rotas FastAPI Consolidadas (`produto_router.py`):**
```python
@router.post("", response_model=ProdutoResponse, status_code=status.HTTP_201_CREATED)
async def criar_produto(payload: ProdutoCreate, admin_id: str = Depends(require_role(["ADMIN", "GESTOR"]))):
    return await produto_service.criar(payload, admin_id)

@router.put("/{produto_id}", response_model=ProdutoResponse)
async def atualizar_produto(produto_id: str, payload: ProdutoUpdate, admin_id: str = Depends(require_role(["ADMIN", "GESTOR"]))):
    # Dívida técnica resolvida: UPDATE implementado e protegido por RBAC server-side
    return await produto_service.atualizar(produto_id, payload, admin_id)

@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_produto(produto_id: str, admin_id: str = Depends(require_role(["ADMIN", "GESTOR"]))):
    await produto_service.soft_delete(produto_id, admin_id)
    return None

```

---

### 5. ARQUITETURA E ADR (15%)

**Diagrama de Componentes**

```text
[ Frontend HTML/JS ] ---> Authorization: Bearer <UUID> ---> [ FastAPI Backend ]
       |-- Verifica RBAC Local                                     |-- Dependência `RequireRole`
       |-- Renderiza CRUD Condicional                              |-- Serializa dados Pydantic
                                                                   v
                                                         [ PostgreSQL (Supabase) ]

```

**ADR-004: Sessões Opacas (UUIDv4)**

* **Status:** ACEITO
* **Decisão:** Optou-se por tokens UUID validados contra a base de dados ao invés de tokens auto-contidos (JWT simples).
* **Consequências:** Garantia de revogação de sessão em tempo real se o usuário for deletado (cascade on delete).

**ADR-005: Soft Delete (Inativação)**

* **Status:** ACEITO
* **Decisão:** A tabela `produtos` recebeu a flag booleana `ativo`. Rotas de listagem públicas e de conversão de orçamentos aplicam filtro `ativo=true`.
* **Consequências:** O banco de dados nunca sofrerá falha de restrição referencial nas ordens de serviço históricas.

---

### 6. VALIDAÇÃO DE SEGURANÇA OWASP (12%)

Os testes práticos exigidos no checklist oficial foram consolidados e comprovam as mitigações implementadas:

**1. A01:2021 – Broken Access Control (RBAC de Mutação)**

* **Vulnerabilidade:** Se a restrição de "editar produtos" ficasse isolada no Javascript (Frontend), vendedores com conhecimento básico de requisições HTTP poderiam emitir comandos PATCH/PUT no backend, adulterando os preços das mercadorias.
* **Implementação:** A injeção estrita da diretiva `Depends(require_role(["ADMIN", "GESTOR"]))` acoplada às funções da API garante a validação da sessão antes do roteamento.
* **Teste de Segurança:**

```bash
curl -i -X PUT "[http://127.0.0.1:8000/produtos/550e8400-e29b-41d4-a716-446655440000](http://127.0.0.1:8000/produtos/550e8400-e29b-41d4-a716-446655440000)" \
     -H "Authorization: Bearer TOKEN_DE_VENDEDOR" \
     -H "Content-Type: application/json" \
     -d '{"preco_venda": 0.01}'

```

*(Status Retornado: 403 Forbidden. A transação é liminarmente bloqueada).*

**2. A03:2021 – Injection (Escapamento Estrutural PostgREST)**

* **Vulnerabilidade:** Devido à estrutura do PostgREST baseada em Query Parameters (`nome=ilike.*{termo}*`), um operador malicioso poderia enviar o texto `Cimento&select=*,custo_oculto` no campo de busca para forçar a exposição de colunas sensíveis na resposta JSON.
* **Implementação:** Foi consolidada a classe utilitária `build_safe_query()`, a qual roda a string através do método URL-Safe do Python, forçando a codificação de caracteres delimitadores (`&` e `=`) em seus formatos hexadecimais seguros.
* **Teste de Segurança:**

```bash
curl -i -X GET "[http://127.0.0.1:8000/produtos/busca?termo=Furadeira&select=*,custo](http://127.0.0.1:8000/produtos/busca?termo=Furadeira&select=*,custo)" \
     -H "Authorization: Bearer TOKEN_VALIDO"

```

*(A API serializa o payload blindado e procura textualmente pelo produto "Furadeira&select...", não retornando nada [lista vazia]. A injeção de parâmetros falha).*

**3. A05:2021 – Security Misconfiguration (Derrubada Limpa de Rota)**

* **Vulnerabilidade:** Caso um usuário ou sistema externo exigisse o `UPDATE` ou o `DELETE` de um ID que não existe na base (ID falso), o Supabase retornaria um erro quebrando a execução do Python (Erro 500), devolvendo ao cliente traços sensíveis da stack do servidor.
* **Implementação:** Os serviços da Sprint foram reescritos em blocos `try/except`. O service intercepta a ausência de registros retornando HTTP 404 (Not Found) padrão.
* **Teste de Segurança:**

```bash
curl -i -X DELETE "[http://127.0.0.1:8000/produtos/00000000-0000-0000-0000-000000000000](http://127.0.0.1:8000/produtos/00000000-0000-0000-0000-000000000000)" \
     -H "Authorization: Bearer TOKEN_GESTOR"

```

*(Status Retornado: 404 Not Found, "Produto não encontrado". Encerramento elegante do processamento).*
