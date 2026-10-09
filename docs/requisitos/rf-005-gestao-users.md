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


## RF-005: GESTÃO DE USUÁRIOS E CONSOLIDAÇÃO MVP

### 1. IDENTIFICAÇÃO DO REQUISITO

**ID:** RF-005   
**Título:** Consolidação MVP v1.0.0 (Gestão de Pessoas e Acessos)   
**Tipo:** Requisito Funcional e de Segurança   
**Prioridade:** ALTÍSSIMA (Entrega do Produto Mínimo Viável)   
**Complexidade:** MÉDIA (5 story points)   
**Status:** CONCLUÍDO
**Data de Criação:** 23/09/2026   
**Última Atualização:** 09/10/2026   

**Breve Descrição:**
O módulo administra funcionários e clientes através de operações CRUD com deleção lógica, consolidando a matriz de privilégios. Além de prover a interface de RH, inclui o painel "Meu Painel" para atualização restrita de dados do próprio operador e alteração segura de credenciais de acesso.

---

### 2. DESCRIÇÃO E ATORES

**Descrição Detalhada e Contexto do Negócio:**
Com a loja rodando, o administrador precisa controlar o acesso de quem entra ou sai da empresa. A inativação de um funcionário demitido revoga o acesso imediatamente ao backend sem apagar a rastreabilidade contábil (soft delete). Simultaneamente, permite-se que o usuário gerencie sua própria senha inicial.

**Objetivos de Negócio (Benefícios):**
1. Conformidade com LGPD garantindo que exclusões bloqueiem o acesso imediatamente (Downtime de inativação < 1 segundo).
2. Proteger 100% da lista de funcionários corporativos contra engenharia social de operadores da ponta (O Vendedor Cego).
3. Centralização da padronização de credenciais, reduzindo em 90% a carga do suporte para cadastro inicial (a aplicação acopla o hash padrão nativamente).

**Atores do Sistema:**

1. **GESTOR / ADMIN (Ator Principal)**
Papel: Administrar a equipe corporativa e acessos.
Permissões:
[X] CREATE (Funcionários novos e Clientes).
[X] READ (Listagem global contendo ativos e inativos).
[X] UPDATE (Atualização e inativação de perfis).
[ ] DELETE (Físico bloqueado, convertendo requisições para Soft Delete).

2. **VENDEDOR (Ator Secundário Restrito)**
Papel: Atendimento de base.
Permissões:
[X] READ / UPDATE (Apenas dados de Clientes da loja). A interface e a API bloqueiam a listagem de funcionários para esse nível.

3. **SISTEMA (Ator Automático)**
Papel: Gerador Hash.
Permissões: Gravar hashes e interceptar sessões mortas de perfis inativos.

---

### 3. ESPECIFICAÇÃO DE CASOS DE USO E REQUISITOS NÃO-FUNCIONAIS

**Caso de Uso (UC-005): Cadastrar Funcionário e Alterar Senha**

**Pré-Condições**
1. Usuário Gestor/Admin com token JWT validado no backend.
2. Coluna `ativo BOOLEAN DEFAULT TRUE` implementada nas tabelas relacionais do PostgreSQL.

**Pós-Condições (Sucesso)**
1. Conta dupla gerada (`users` + `pessoas`) com integração UUID.
2. Senhas alteradas extraindo o alvo diretamente do JWT (sem input exposto na API).

**Pós-Condições (Falha)**
1. Tentativa de escalonamento vertical (Ex: Gestor tentar criar Admin) bloqueada com Erro 403.

**Fluxo Principal (Criação de Conta)**
1. O Gestor acessa "Gestão de Pessoas" e clica no botão "+ Novo Funcionário".
2. O Frontend aciona o modal e o Gestor preenche Nome, E-mail e escolhe a Role (VENDEDOR).
3. O Frontend dispara `POST /usuarios` repassando o payload sem senha.
4. O Backend FastAPI intercepta, verifica se o requerente tem autorização (`RequireRole`).
5. O Backend gera o hash `bcrypt` para a senha corporativa oficial ("senha123").
6. O Backend insere na tabela `users` recuperando o UUID.
7. O Backend insere na tabela `pessoas`, vinculando o UUID recém-gerado.
8. O Frontend atualiza a listagem dinamicamente e notifica o sucesso.

**Fluxos Alternativos**
* **A1: O Vendedor Cego:** Um Vendedor acessa a tela de Gestão. O frontend desabilita botões. Ele chama `GET /pessoas`. O backend capta a role e embute um comando restritivo `user_id IS NULL`. O vendedor só recebe e enxerga clientes físicos, nunca funcionários.
* **A2: Inativação LGPD (Soft Delete):** O Gestor aciona "Excluir" em um funcionário. A API roda `UPDATE pessoas SET ativo = false`. O operador inativado tem a validação de middleware do FastAPI abortada na próxima vez que clicar em qualquer tela do ERP (Erro 401), protegendo as vendas.
* **A3: Troca Stateful de Senha:** O usuário acessa Meu Painel. Preenche Senha Atual e Nova Senha (2x). O endpoint `PATCH /auth/senha` é acionado **sem enviar o ID** no JSON. O backend extrai o ID criptograficamente do token e aplica a atualização.

**Regras de Negócio (RN)**

| ID | Regra | Descrição |
|---|---|---|
| RN-01 | Dualidade Relacional | Um funcionário requer linhas ativas e correlacionadas nas tabelas `users` e `pessoas`. Um cliente comum exige linha apenas em `pessoas`. |
| RN-02 | Injeção Hash Inicial | É terminantemente proibido enviar senhas limpas na criação de usuários. O hash corporativo ocorre exclusivamente em memória RAM pelo Backend. |
| RN-03 | Escalonamento Bloqueado | Regra cruzada de segurança garante que nível Gestor jamais consiga aprovar a submissão de perfis de nível Admin. |

**Requisitos Não-Funcionais (RNF)**

| ID | Atributo | Requisito | Métrica | Justificativa |
|---|---|---|---|---|
| RNF-01 | Reusabilidade | Integração de Interface | 100% de reaproveitamento do script `header.js` nas novas telas de Gestão. | Reduz carga de manutenção frontal. |
| RNF-02 | Segurança | Validação Sensível | A senha não deve ter menos de 6 caracteres na troca e precisa ser analisada no parser Pydantic < 100ms. | Bloquear senhas brutas fracas na porta. |

---

### 4. PROTÓTIPO FUNCIONAL E CÓDIGO (50%)

**Aviso de Evolução de Sprint:**
Conforme ressaltado nas correções das sprints, o Frontend não possuía documentação e testes conclusivos[cite: 38]. Esse módulo entregou formalmente as telas `gestaoPessoas.html` e `meuPainel.html`, garantindo todas as ações restritivas e integrando a listagem de funcionários pendente. 

**Persistência Completa de Backend:**
O repositório `usuarios_repository.py` processa ativamente o DDL criado para interconexão e devolução de 201 Created:
```python
def criar_usuario_funcionario(nome: str, email: str, role: str, password_hash: str):
    # Requisição segura via RPC assegurando a injeção da senha do backend
    payload = {"p_nome": nome, "p_email": email, "p_cpf": None, "p_user_role": role, "p_password_hash": password_hash}
    client.post("/rest/v1/rpc/rf005_criar_usuario_funcionario", json=payload)

```

---

### 5. ARQUITETURA E ADR (15%)

**Diagrama de Componentes**

```text
[ Painel do Usuário ] ---> PATCH /auth/senha ---> [ FastAPI (Depends Token) ]
        |                                                 |-- Extrai ID do Token
        |                                                 |-- Pydantic length validator
        v                                                 v
(Ação JS: Validate match)                            [ PostgreSQL Update ]

```

**ADR-015: Proteção Stateful na Troca de Senha**

* **Status:** ACEITO
* **Decisão:** Remover parâmetros de ID explícitos (query parameters ou body JSON) das rotas de troca de senha e dados sensíveis. O ID requisitado agora deve ser extraído invariavelmente através do contexto decodificado do Token pelo Middleware.
* **Consequências:** Zero risco de manipulação de requisição cross-user (BOLA).

**ADR-016: O Vendedor Cego (Backend for Frontend)**

* **Status:** ACEITO
* **Decisão:** Em vez de filtrar a tela no frontend com HTML (o que vazaria dados corporativos via Network Tab no Chrome), o filtro foi movido para o Backend. Se a role é Vendedor, a API recusa despachar dados corporativos.
* **Consequências:** Conformidade forte de isolamento de dados departamentais.

**ADR-017: Soft Delete Integrado**

* **Status:** ACEITO
* **Decisão:** Executou-se a alteração de esquema para adicionar `ativo BOOLEAN` em vez de DELETE em cascata, protegendo a rastreabilidade fiscal.

---

### 6. VALIDAÇÃO DE SEGURANÇA OWASP (12%)

Nesta consolidação, a suíte OWASP demandada pela revisão do projeto cobriu especificamente controle de sessão, vazamento de senhas e BOLA.

**1. A01:2021 – Broken Access Control / BOLA (Vendedor Cego)**

* **Vulnerabilidade:** Se um usuário Vendedor solicitasse `GET /pessoas`, ele veria os dados internos de todos os administradores e gerentes na aba Network do DevTools.
* **Implementação:** A camada Service examina a string JWT. Ao detectar a label `VENDEDOR`, o Python manipula o Supabase Client concatenando imperativamente o filtro: `.eq("user_id", "is.null")`.
* **Teste (Prova de Isolamento):**

```bash
curl -X GET "[http://127.0.0.1:8000/pessoas](http://127.0.0.1:8000/pessoas)" \
     -H "Authorization: Bearer TOKEN_VENDEDOR"

```

*(Status Retornado: 200 OK. Contudo, 100% dos JSON retornados têm a chave `"user_id": null`. O vendedor atendeu sua requisição, mas ficou "cego" para os dados corporativos da empresa).*

**2. A04:2021 – Insecure Design (Lógica na Troca de Credenciais)**

* **Vulnerabilidade:** A ausência de validação estrutural permitiria aos colaboradores trocarem senhas para `"123"` ou sobrescreverem a mesma senha seguidas vezes.
* **Implementação:** O schema `Pydantic` aplica `min_length=6` bloqueando strings curtas de chegarem ao núcleo `bcrypt`. O módulo de negócio checa igualdade lógica, emitindo erro 400 se as senhas coincidirem.
* **Teste (Falha Lógica Rejeitada):**

```bash
curl -X PATCH "[http://127.0.0.1:8000/auth/senha](http://127.0.0.1:8000/auth/senha)" \
     -H "Authorization: Bearer TOKEN_VALIDO" \
     -H "Content-Type: application/json" \
     -d '{"senha_atual": "senha123", "nova_senha": "123"}'

```

*(Status Retornado: 422 Unprocessable Entity - `String should have at least 6 characters`, garantindo padrão rigoroso corporativo).*

**3. A07:2021 – Identification and Authentication Failures (Revogação de Conta LGPD)**

* **Vulnerabilidade:** Contas inativadas pelo RH por soft-delete (sem deleção física no banco) continuariam utilizando Tokens validados que ainda possuíssem tempo de vida (Sessões Zumbis).
* **Implementação:** O injetor `Depends(get_current_user)` não apenas valida a criptografia do Token, mas executa um ping real-time no banco confirmando se `users.ativo == true`. A inativação na tela Gestor reverte a sessão em milissegundos.
* **Teste (Sessão Zumbi Capturada):**

1. Usuário faz login e guarda o Token gerado e válido no Header.
2. O Gestor deleta (inativação lógica) o usuário no Frontend.
3. Usuário tenta listar o estoque usando o Token que era válido:

```bash
curl -X GET "[http://127.0.0.1:8000/produtos](http://127.0.0.1:8000/produtos)" \
     -H "Authorization: Bearer TOKEN_ZUMBI"

```

*(Status Retornado: 401 Unauthorized - O banco confirmou a exclusão e derrubou o JWT instantaneamente).*
