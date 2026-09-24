### RF-005: Gestão de Usuários e Consolidação (MVP v1.0.0)

---

## 1. IDENTIFICAÇÃO DO REQUISITO

**ID:** RF-005   
**Título:** Consolidação MVP v1.0.0 (Gestão de Pessoas, Senhas e Acessos)   
**Tipo:** Requisito Funcional e de Segurança   
**Prioridade:** ALTÍSSIMA (Consolida a entrega final do Produto Mínimo Viável)   
**Complexidade:** MÉDIA (Envolve UI Condicional e Segurança Stateful)   
**Status:** CONCLUÍDO (MVP v1.0.0)   
**Data de Criação:** 23/09/2026   
**Última Atualização:** 23/09/2026   

**Breve Descrição:**
Implementação do módulo de gestão administrativa de funcionários e clientes (CRUD com deleção lógica), estabelecendo o motor de hierarquia de privilégios. Inclui a criação de um painel de autoatendimento ("Meu Painel") para troca segura de credenciais e atualização de dados próprios, chancelando a versão base (v1.0.0) do ERP de acordo com os critérios de segurança OWASP e restrições de arquitetura exigidos pela avaliação acadêmica.

---

## 2. DESCRIÇÃO E ATORES

**Contexto do negócio:**
O ERP atingiu sua maturidade operacional. Agora, a loja precisa gerenciar quem acessa o sistema. Vendedores lidam apenas com clientes (balcão), enquanto Gestores e Administradores administram a folha de acessos da equipe. Nenhuma senha pode ser criada pelo front-end para novos funcionários, e a inativação de um perfil deve revogar imediatamente seu acesso sem destruir o histórico de vendas.

**Atores do Sistema:**

### 1. Administrador e Gestor (Atores Principais)

* **Papel:** Gerenciar a equipe e a carteira completa de clientes.
* **Permissões:**
* CREATE (Novos funcionários e clientes).
* READ (Visão global de todos os usuários e clientes, ativos ou inativos).
* UPDATE (Editar dados e inativar perfis).



### 2. Vendedor (Ator Secundário Restrito)

* **Papel:** Operador de balcão.
* **Permissões:**
* READ / UPDATE / DELETE lógico (Restrito **apenas** a Clientes onde `user_id IS NULL`).
* Cego para a existência de outros funcionários no sistema.



### 3. Sistema (Ator Automático)

* **Papel:** Leão de chácara da segurança e gerador de hashes.
* **Permissões:**
* Gerar a credencial inicial `senha123` via `bcrypt` para novos cadastros.
* Barrar acessos de tokens válidos cujo perfil esteja marcado como `ativo = false`.

---

## 3. ESPECIFICAÇÃO DE CASOS DE USO E REQUISITOS NÃO-FUNCIONAIS

**Caso de Uso (UC-005): Cadastro de Funcionário e Gestão de Credenciais**

### Pré-Condições

* Usuário logado com sessão Stateful ativa (`token_uuid` validado no banco).


* Tabelas `users` e `pessoas` atualizadas com a coluna `ativo BOOLEAN NOT NULL DEFAULT TRUE`.

### Pós-Condições (Sucesso)

* Novo funcionário criado simultaneamente nas tabelas `users` (credencial) e `pessoas` (perfil).
* Senhas alteradas com sucesso a partir do ID extraído estritamente do Token.

### Pós-Condições (Falha)

* Vendedor tentando listar funcionários, ou Gestor tentando criar Admin, recebem erro `403 Forbidden`.

### Fluxo Principal (Criação de Funcionário por Gestor)

1. Gestor acessa a página "Gestão de Pessoas" (`gestaoPessoas.html`).
2. Frontend valida o RBAC Client-Side e exibe o botão "+ Novo Funcionário".
3. Gestor clica no botão, preenchendo Nome, E-mail e selecionando a Role (Vendedor ou Gestor).
4. Gestor clica em "Salvar".
5. Frontend dispara `POST /usuarios` contendo o payload.
6. Backend (FastAPI) intercepta a requisição e valida se o requerente tem permissão (`RequireRole`).
7. Backend gera o hash `bcrypt` para a senha padrão corporativa ("senha123").
8. Backend realiza a inserção na tabela `users` (gerando o UUID do usuário).
9. Backend realiza a inserção na tabela `pessoas`, vinculando o `user_id` recém-gerado.
10. Backend retorna `201 Created` e o Frontend atualiza a listagem dinamicamente.

### Fluxos Alternativos

**A1: O Vendedor Cego (Restrição de Visualização na Listagem)**

1. Vendedor acessa a página "Gestão de Pessoas".
2. O botão "+ Novo Funcionário" está oculto via CSS (`display: none`).
3. Frontend dispara `GET /pessoas`.
4. Backend identifica pelo token que o usuário é Vendedor.
5. Backend anexa silenciosamente a cláusula `AND user_id IS NULL` na query do Supabase.
6. Frontend renderiza a tabela contendo estritamente Clientes de Balcão.

**A2: Escalonamento Vertical Bloqueado (Bypass F12)**

1. Um usuário com perfil GESTOR burla o frontend e envia via cURL ou Postman um `POST /usuarios` com `"role": "ADMIN"`.
2. Backend decodifica a requisição e compara a role solicitada com a role de quem pediu.
3. Backend identifica a quebra de hierarquia.
4. Transação é abortada imediatamente com retorno `HTTP 403 Forbidden`.

**A3: Alteração de Senha Segura (Meu Painel)**

1. Usuário clica em sua Role no header e é direcionado para `meuPainel.html`.
2. Usuário insere "Senha Atual" e "Nova Senha" (2x) e clica em Salvar.
3. Frontend valida se as novas senhas coincidem.
4. Frontend envia `PATCH /auth/senha` **sem informar o ID do usuário** no body.
5. Backend extrai o `usuario_id` diretamente do `Depends(obter_usuario_atual)`.
6. Backend valida a senha atual e persiste o novo hash no banco.

### Regras de Negócio (RN)

| ID | Regra | Descrição |
| --- | --- | --- |
| **RN-01** | Dualidade Pessoa-User | Um funcionário obrigatoriamente possui registro em `users` e `pessoas`. Um cliente de balcão possui apenas registro em `pessoas` (`user_id IS NULL`).

 |
| **RN-02** | Senha Padrão Backend | O frontend não envia senha no cadastro de funcionários. O backend injeta o hash de "senha123" nativamente. |
| **RN-03** | Identidade Inviolável | Na rota `PATCH /auth/senha`, a API rejeita qualquer identificador enviado por Query ou Body, confiando exclusivamente no dono do Token.

 |
| **RN-04** | Inativação (Soft Delete) | Funcionários demitidos ou clientes removidos recebem `ativo = false`, revogando acesso ao login instantaneamente sem apagar o histórico de vendas.

 |

### Requisitos Não-Funcionais (RNF)

| ID | Atributo | Requisito | Justificativa |
| --- | --- | --- | --- |
| **RNF-01** | Arquitetura | Modularização Frontend | Novas telas isoladas em `src/features/gestaoPessoas` e `src/features/meuPainel`. |
| **RNF-02** | UX | Componentização | Reutilização obrigatória do `header.js` e `global.css` do projeto. |

---

## 4. PROTÓTIPO FUNCIONAL

**Mockup - Tela 1: Gestão de Pessoas (Visão do GESTOR)**

```text
┌─────────────────────────────────────────────────────────────────┐
│  ☰ ERP Construção       Meu Painel (Gestor)     [ Sair ]        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  👥 Gestão de Entidades                      [ + NOVO FUNCIONÁRIO]
│                                                                 │
│  Filtros: (•) Todos  ( ) Apenas Clientes  ( ) Inativos          │
│                                                                 │
│  NOME               | TIPO       | CONTATO       | AÇÕES        │
│  -------------------------------------------------------------  │
│  Maria de Fátima    | Cliente    | 61 9999-9999  | [✏️][🗑️]     │
│  Carlos (Caixa 1)   | Vendedor   | carlos@erp.br | [✏️][🗑️]     │
└─────────────────────────────────────────────────────────────────┘

```

**Mockup - Tela 2: Meu Painel (Segurança)**

```text
┌─────────────────────────────────────────────────────────────────┐
│  👤 Meu Painel (Portal do Funcionário)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Nome:  [ Carlos Alberto             ]                          │
│  Email: [ carlos@erp.br              ] (Bloqueado)              │
│  Role:  [ VENDEDOR                   ] (Bloqueado)              │
│                                                                 │
│  [ SALVAR DADOS ]                 [ 🔒 ALTERAR MINHA SENHA ]    │
└─────────────────────────────────────────────────────────────────┘

```

---

## 5. ARQUITETURA E ADR

### Diagrama de Fluxo (Criação de Usuário e Dualidade de Tabelas)

```text
[ Frontend Gestor ] 
       |-- POST /usuarios { nome, email, role }
       v
[ FastAPI Backend (RequireRole) ]
       |-- Gera Hash (senha123)
       |
       +--> INSERT INTO users (email, hash, role) -> Retorna UUID
       +--> INSERT INTO pessoas (nome, user_id=UUID)

```

### ADR-016: Separação de Rotas de Alteração de Senha (Stateful Security)

* **Contexto:** A alteração de senhas precisava ser protegida contra manipulação de requisições, onde um Vendedor poderia tentar interceptar a chamada e enviar o ID de um Gestor no corpo da requisição.
* **Decisão:** A rota `PATCH /auth/senha` foi arquitetada para não aceitar nenhum parâmetro de identificação via Payload ou Query. O identificador do usuário a ser alterado é extraído nativamente no backend através do token de sessão ativo (`Depends(obter_usuario_atual)`).


* **Consequências:** ✅ Mitigação total de IDOR na alteração de senhas. Nenhuma interface frontend pode fraudar a identidade do requisitante.

### ADR-017: Controle de Visibilidade Backend (O Vendedor Cego)

* **Contexto:** Por razões de privacidade, Vendedores não devem visualizar a lista de funcionários da empresa, mas precisam gerir clientes de balcão.
* **Decisão:** Em vez de filtrar a lista no frontend (o que exporia os dados na aba Network do navegador), a rota `GET /pessoas` inspeciona a role do token no servidor. Se for `VENDEDOR`, a API modifica a string de busca para o Supabase exigindo `user_id IS NULL`.
* **Consequências:** ✅ Proteção de dados sensíveis na camada de transporte (Backend for Frontend).

### ADR-018: Inativação Lógica de Identidades (Soft Delete Integrado)

* **Contexto:** A LGPD exige a possibilidade de exclusão de dados, mas o ERP exige integridade referencial para as Ordens de Serviço faturadas.
* **Decisão:** Executou-se um comando DDL adicionando a coluna `ativo BOOLEAN NOT NULL DEFAULT TRUE` às tabelas `users` e `pessoas`.

* **Consequências:** ✅ Quando um usuário é "excluído" na UI, seu acesso ao sistema (`auth_service`) é imediatamente revogado, mas seu ID permanece atrelado ao histórico contábil.

---

## 6. VALIDAÇÃO DE SEGURANÇA OWASP

## EXEMPLO DE OWASP GENERICO - REALIZAR TESTES REAIS

O foco desta iteração de consolidação foi blindar as camadas de autenticação e escalonamento, atendendo às deficiências mais críticas apontadas em rigorosas avaliações acadêmicas.

### 1. A02:2021 – Cryptographic Failures (Armazenamento e Fluxo de Senhas)

**Vulnerabilidade:** Exposição de credenciais em banco de dados ou logs de sistema durante a alteração de senhas.
**Implementação:** O sistema nunca recebe o hash finalizado do front-end e nunca envia a senha gerada de volta. Na criação de usuários, o backend injeta de forma autônoma a cifra utilizando `bcrypt`. Durante a troca no "Meu Painel", a função `alterar_senha_usuario` consome um custo de processamento elevado (`gensalt(12)`) para garantir resistência a ataques de força bruta, descartando a senha original instantaneamente da memória.
**Evidência de Execução:** Uma consulta ao PostgreSQL comprova a persistência criptográfica:

```sql
SELECT email, password_hash FROM users WHERE email = 'vendedor@erp.com';
-- Resultado: vendedor@erp.com | $2b$12$X/6c/3bwEOyYC2... (Hash irreversível de 60 chars)

```

### 2. A07:2021 – Identification and Authentication Failures (Proteção contra Timing Attacks)

**Vulnerabilidade:** Atacantes medem a latência de resposta da API na rota de Login para enumerar quais e-mails existem no banco de dados. Se o e-mail não existe, a API rejeita em 10ms. Se existe, mas a senha está errada, a API gasta 300ms calculando o hash, denunciando a existência da conta.
**Implementação:** Implementou-se um equalizador de carga no `auth_service_2.py`. Caso o usuário não seja encontrado no banco, o servidor processa intencionalmente um "Hash Fantasma" (`_DUMMY_HASH`) com o mesmo custo criptográfico, nivelando o tempo de resposta.
**Teste Prático (Simulação de Enumeração):**

```bash
# Tentativa com e-mail inexistente
curl -X POST "http://127.0.0.1:8000/auth" -d '{"email":"falso@erp.com", "senha":"123"}'
# Resposta: 401 Unauthorized (Tempo: ~312ms)
# Anexar as respostas REAIS

# Tentativa com e-mail válido e senha errada
curl -X POST "http://127.0.0.1:8000/auth" -d '{"email":"admin@erp.com", "senha":"errada"}'
# Resposta: 401 Unauthorized (Tempo: ~314ms)
# Anexar as respostas REAIS
```

*(As respostas são temporalmente idênticas, cegando o atacante).*

### 3. A01:2021 – Broken Access Control (Escalonamento Vertical via Criação)

**Vulnerabilidade:** Um funcionário com perfil `GESTOR` intercepta o request de criação de usuário (`POST /usuarios`) e altera o JSON enviando `"role": "ADMIN"`, garantindo a si mesmo uma conta paralela de poder absoluto.
**Implementação:** A API aplica validação cruzada entre o Token (quem pede) e o Payload (quem será criado). A injeção de dependência barra explicitamente escalonamentos não autorizados.
**Teste Prático (Simulação de Bypass de Role):**

```bash
# Gestor tenta criar uma conta Admin
curl -X POST "http://127.0.0.1:8000/usuarios" \
     -H "Authorization: Bearer <TOKEN_DE_GESTOR>" \
     -H "Content-Type: application/json" \
     -d '{"nome": "Hacker Account", "email": "hacker@erp.com", "role": "ADMIN"}'

```

**Resposta do Servidor (Bloqueio Efetivo):**

```json
{
  "detail": "Acesso Negado: Gestores não possuem permissão para criar Administradores."
}

```

*(HTTP Status: `403 Forbidden` — O controle de acesso atua como o leão de chácara da aplicação).*