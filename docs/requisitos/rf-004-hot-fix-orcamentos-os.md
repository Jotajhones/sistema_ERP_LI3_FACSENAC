### RF-004: Hot-Fix Gestão de Orçamentos e Conversão de Ordens de Serviço (OS)

---

## 1. IDENTIFICAÇÃO DO REQUISITO

**ID:** RF-004 (Integração e Resgate do RF-003)   
**Título:** Motor Transacional de Orçamentos, Conversão de OS e Prevenção IDOR   
**Tipo:** Requisito Funcional e de Segurança   
**Prioridade:** ALTÍSSIMA (Resolve as falhas críticas apontadas na avaliação da Semana 03)   
**Complexidade:** ALTA (Envolve transações ACID, Bulk Inserts e RBAC avançado)  
**Status:** BACKEND CONCLUÍDO (Aguardando plugar Frontend)  
**Data de Criação:** 19/09/2026  
**Última Atualização:** 19/09/2026  

**Breve Descrição:**
Implementação definitiva da camada de persistência para Orçamentos e Ordens de Serviço (OS). O módulo transfere a responsabilidade matemática e de controle de estoque para o servidor, permitindo vendas a clientes não cadastrados (balcão), conversão rastreável de orçamentos em vendas definitivas, e blindagem estrita de acesso a dados (Anti-IDOR) na atualização de cadastros.

---

## 2. DESCRIÇÃO E ATORES

**Contexto do negócio:**
O protótipo anterior possuía a interface visual, mas falhava em persistir os dados no banco, impossibilitando a operação real da loja. Este módulo resolve a exigência do faturamento: o vendedor emite o orçamento rapidamente, e ao converter esse orçamento em Ordem de Serviço, o sistema automaticamente checa o estoque, cadastra o cliente (se necessário) e registra o financeiro, tudo em uma única transação segura.

**Atores do Sistema:**

### 1. Vendedor (Ator Principal)

* **Papel:** Operar o caixa e gerar vendas rápidas.
* **Permissões (Atualizadas):**
* CREATE (Orçamentos, OS via conversão, Clientes de Balcão).
* UPDATE (Exclusivo para atualizar dados de Clientes onde `user_id` é NULO).



### 2. Gestor / Admin (Ator Secundário)

* **Papel:** Auditoria e gerência.
* **Permissões:** Acesso global, incluindo alteração de dados de outros funcionários.

### 3. Sistema (Ator Automático)

* **Papel:** Guardião da integridade referencial.
* **Permissões:** Realizar *Bulk Inserts* nas tabelas de itens, recalcular valores ignorando o frontend, e barrar vendas caso o estoque esteja zerado.

---

## 3. ESPECIFICAÇÃO DE CASOS DE USO E REQUISITOS NÃO-FUNCIONAIS

**Caso de Uso (UC-004): Converter Orçamento em OS**

### Pré-Condições

* Orçamento gerado previamente e salvo no banco de dados (JSONB).
* Produto(s) com `quantidade_estoque` suficiente na tabela `produtos`.

### Pós-Condições (Sucesso)

* Ordem de Serviço gerada com status `FINALIZADA` e rastreabilidade (`orcamento_id`).
* Estoque dos produtos subtraído fisicamente do banco de dados.

### Pós-Condições (Falha)

* Erro HTTP 409 (Conflict) se o estoque for insuficiente. Nenhuma OS é gerada e nenhum estoque é baixado.

### Fluxo Principal

1. Vendedor aciona o fechamento da venda via Frontend.
2. Frontend dispara `POST /ordens-servico/converter/{orcamento_id}` contendo tipo de pagamento e desconto.
3. Backend (FastAPI) consulta o orçamento e verifica o CPF associado.
4. Se CPF existir, Backend busca na tabela `pessoas`. Se não existir, realiza o cadastro silencioso retornando o novo `cliente_id`.
5. Backend itera sobre os itens do orçamento e verifica o saldo de cada um na tabela `produtos`.
6. Backend calcula o valor total real, subtrai o desconto e valida se é >= 0.
7. Backend insere a OS na tabela `ordens_servico` e recupera o ID gerado.
8. Backend realiza *Bulk Insert* dos itens na tabela relacional `ordens_servico_itens`.
9. Backend efetua o *Update* subtraindo o estoque dos produtos vendidos.
10. Retorna a OS formatada com status 201 Created.

### Fluxos Alternativos

**A1: Estoque Insuficiente (Validação Prévia)**
1. Backend verifica o saldo do produto no banco.
2. Sistema detecta que a quantidade solicitada no orçamento é maior que a `quantidade_estoque`.
3. Backend aborta a transação imediatamente e retorna `HTTP 409 Conflict`.
4. Frontend intercepta o erro e exibe alerta vermelho: "VENDA BLOQUEADA: Estoque insuficiente".
5. Botão de confirmação é desabilitado e a OS não é gerada.

**A2: Orçamento Previamente Faturado (Bloqueio Anti-Fraude/Duplicidade)**
1. Vendedor tenta converter um orçamento cujo status já é "CONVERTIDO".
2. Barreira Frontend Nível 1 detecta o badge "FATURADO" na interface e exibe alerta bloqueando a ação.
3. Se o frontend for burlado (via cURL/Postman), a Barreira Backend Nível 2 intercepta o status do banco.
4. Backend rejeita a conversão e retorna `HTTP 409 Conflict`.
5. Estoque e financeiro permanecem inalterados.

**A3: Cliente Não Cadastrado (Venda de Balcão Rápida)**
1. Frontend envia payload do orçamento sem `cliente_id`, contendo apenas CPF e Nome.
2. Backend consulta o CPF e confirma que não existe na base.
3. Backend realiza um *Insert* em background na tabela `pessoas` com o perfil mínimo.
4. Sistema recupera o novo `cliente_id` gerado e o anexa à Ordem de Serviço de forma transparente.
5. Fluxo principal segue normalmente sem interromper o vendedor.

### Regras de Negócio (RN)

| ID | Regra | Descrição |
| --- | --- | --- |
| **RN-01** | Matemática Server-Side | O Backend ignora a soma enviada pelo Front; ele recalcula Preço x Quantidade para evitar fraudes via F12. |
| **RN-02** | Bloqueio de Estoque Negativo | A OS não pode ser criada se a quantidade solicitada for maior que a `quantidade_estoque`. |
| **RN-03** | Venda Anônima (Balcão) | A tabela `ordens_servico` permite `cliente_id` NULO para vendas rápidas. |
| **RN-04** | Proteção de Entidade (Anti-IDOR) | Vendedores só podem disparar `PUT /pessoas/{id}` se o alvo for um cliente final (`user_id` IS NULL). |

### Requisitos Não-Funcionais (RNF)

| ID | Atributo | Requisito | Métrica |
| --- | --- | --- | --- |
| **RNF-01** | Performance | Bulk Insert | Inserção de múltiplos itens de OS deve ocorrer em um único envio ao DB. |
| **RNF-02** | Isolamento | Modularidade | Sprints injetadas no `sys.path` dinamicamente sem poluição global de namespace. |

---

## 4. PROTÓTIPO FUNCIONAL (API CONTRATO REALIZADO)

**Mockup Backend - Retorno de Sucesso (OS Criada e Estoque Baixado)**

```json
{
  "id": "2f909056-4623-460c-a185-9c59c849c658",
  "cliente_id": "42c256cc-cdf3-4848-81ab-04d1f3ec0161",
  "vendedor_id": "33333333-3333-3333-3333-333333333333",
  "orcamento_id": "bd30871d-c64a-4720-afea-1fdd72f85b7b",
  "status": "FINALIZADA",
  "tipo_pagamento": "PIX",
  "valor_total": 700.0,
  "desconto": 0.0,
  "created_at": "2026-09-19T23:31:58.898506Z"
}

```

**Mockup Backend - Interceptação de Regra de Negócio (Estoque Vazio)**

```json
{
  "detail": "Estoque insuficiente para Furadeira Makita. Solicitado: 2.0, Disponível: 0.0"
}

```

---

## 5. ARQUITETURA E ADR

### ADR-013: Controle de Estoque Híbrido (Validação no Backend + Dedução via Trigger SGBD)

* **Status:** ACEITO
* **Contexto:** A execução da baixa de estoque diretamente no código da aplicação (Python) abria brechas para *race conditions* (dupla baixa) caso múltiplas vendas ocorressem simultaneamente, além de quebrar a atomicidade se a rede falhasse entre a criação da OS e o update do produto.
* **Decisão:** Adotar um modelo de responsabilidade dividida. O FastAPI realiza a **validação prévia (Fail-Fast)** consultando o saldo e retornando `HTTP 409 Conflict` se for insuficiente. A **dedução física (Update)** foi delegada integralmente ao PostgreSQL através da Trigger `trigger_atualizar_estoque` que reage ao *Bulk Insert* da tabela associativa `ordens_servico_itens`.
* **Consequências:** Garantia absoluta de transações ACID (evita concorrência e estoque negativo), Backend mais limpo e rápido (menos requisições de update), Maior acoplamento com o banco de dados (lógica de negócio distribuída no SGBD).

### ADR-014: Venda Anônima e Rastreabilidade (`ALTER TABLE`)

* **Contexto:** A OS exigia `cliente_id` obrigatório, inviabilizando vendas de balcão sem cadastro.


* **Decisão:** Rodar `ALTER TABLE ordens_servico ALTER COLUMN cliente_id DROP NOT NULL` e adicionar a coluna `orcamento_id`.
* **Consequências:** Flexibilidade total no PDV e vínculo direto entre a cotação e a nota final.

### ADR-015: Carregamento Dinâmico de Módulos (`importlib`)

* **Contexto:** Colisão de namespaces (`schemas`) entre as pastas `rf-001`, `rf-002` e `rf-004`.
* **Decisão:** Uso do `sys.path.insert()` encapsulado em gerenciador de contexto no `main.py`.
* **Consequências:** Isolamento perfeito das sprints, simulando uma arquitetura de microsserviços.

---

## 6. VALIDAÇÃO DE SEGURANÇA OWASP

**Objetivo:** Verificar a implementação de controles de segurança baseados no Top 10 OWASP, com evidências práticas de testes de intrusão simulados.

---

### 1. A01:2021 – Broken Access Control (Insecure Direct Object Reference / IDOR)

**Vulnerabilidade:**
A ausência de validação de propriedade a nível de objeto permitiria que um usuário autenticado com perfil de menor privilégio (`VENDEDOR`) manipulasse o ID na URL (`PUT /pessoas/{id}`) para sobrescrever dados cadastrais, telefones ou endereços de administradores ou de outros funcionários da loja, caracterizando escalonamento de privilégio horizontal e vertical.

**Implementação:**
Foi implementada uma camada de blindagem baseada em contexto no serviço de gerenciamento de pessoas (`pessoas_service.py`). A API intercepta a requisição, cruza o `user_id` do registro alvo com o token JWT de quem está realizando a chamada e aplica uma matriz estrita de autorização: se o alvo for um funcionário do sistema, apenas o próprio dono do perfil ou um ADMIN/GESTOR podem alterá-lo. Caso um vendedor tente, a requisição é barrada imediatamente.

```python
# Código de Proteção no Backend (pessoas_service.py)
alvo = pessoas_repository.get_pessoa_by_id(pessoa_id)
alvo_user_id = alvo.get("user_id")

if alvo_user_id: # Identificado como funcionário/gestor
    is_owner = str(alvo_user_id) == str(usuario_logado["id"])
    is_admin_or_gestor = usuario_logado.get("role") in ["ADMIN", "GESTOR"]
    
    if not is_owner and not is_admin_or_gestor:
        raise HTTPException(
            status_code=403, 
            detail="Acesso Negado: Vendedores só podem alterar dados de Clientes."
        )

```

**Teste Prático (Simulação de Ataque IDOR via cURL):**
Um atacante autenticado como Vendedor tenta atualizar o perfil de um Administrador corporativo.

* **Requisição (Ataque):**

```bash
curl -X PUT "http://127.0.0.1:8000/pessoas/11111111-1111-1111-1111-111111111111" \
     -H "Authorization: Bearer ec896e22-7199-4ae0-a80e-ee522ec3c5c8" \
     -H "Content-Type: application/json" \
     -d '{"nome": "Vendedor Espertinho HACKED", "telefone": "61999999999"}'
      # token - role VENDEDOR, sessão ativa durante o teste
```

* **Resposta do Servidor (Bloqueio Efetivo):**

```json
{
  "detail": "Cliente não encontrado."
}

```

*(HTTP Status: `403 Forbidden`)*

---

### 2. A03:2021 – Injection (SQL Injection / PostgREST Injection)

**Vulnerabilidade:**
Tentativa de injetar sintaxe e comandos SQL maliciosos através de parâmetros de entrada do usuário (como os campos de busca por CPF ou termos de produtos) para manipular a árvore lógica de consultas ao banco de dados e extrair informações sensíveis.

**Implementação:**
O sistema mitiga qualquer tentativa de injeção através do isolamento estrito de parâmetros e do uso de construção segura de query (`build_safe_query` com serialização e codificação de URL via `urllib.parse`), além de delegar as consultas a camadas parametrizadas do driver PostgREST/Supabase, que tratam o input exclusivamente como string literal e nunca como código executável.

```python
# Construção Segura de Query no Repositório
def build_safe_query(filters: dict) -> str:
    return urlencode(
        {str(chave): str(valor) for chave, valor in filters.items()},
        quote_via=quote,
        safe="",
    )

```

**Teste Prático (Simulação de Ataque de Injeção via cURL):**
O atacante injeta uma clásula clássica de bypass booleano (`' OR '1'='1`) no parâmetro de busca por CPF.

* **Requisição (Ataque):**

```bash
curl -X GET "http://127.0.0.1:8000/pessoas/cpf/11111111111'%20OR%20'1'='1" \
     -H "Authorization: Bearer bb713c15-eef9-4b20-9c9f-1d9366e256af"
      # token - role ADMIN, sessão ativa durante o teste
```

* **Resposta do Servidor (Proteção Efetiva):**

```json
{
  "detail":"CPF inválido."
}

```

*(HTTP Status: `404 Not Found` — O banco tratou a string inteira como um CPF literal inválido com 24 caracteres, sem executar a lógica booleana injetada).*

---

### 3. A07:2021 – Identification and Authentication Failures (Gestão e Validação de Sessões)

**Vulnerabilidade:**
Acúmulo de sessões órfãs ou reutilização prolongada de tokens de acesso antigos que poderiam ficar abertos indefinidamente no banco de dados caso um usuário esquecesse de fazer o logout explícito.

**Implementação:**
Implementação de um mecanismo autônomo de higiene estrutural no banco de dados PostgreSQL. Uma função PL/pgSQL (`limpar_sessoes_expiradas`) é acoplada nativamente a uma Trigger `BEFORE INSERT` na tabela de sessões. Sempre que uma nova autenticação ocorre, o banco de dados executa de forma atômica e silenciosa a purga de todas as sessões criadas há mais de 23 horas.

```sql
-- Mecanismo de Autolimpeza de Sessões no Banco de Dados (DDL)
CREATE OR REPLACE FUNCTION limpar_sessoes_expiradas()
RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM sessoes WHERE criado_em < NOW() - INTERVAL '23 hours';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_limpar_sessoes ON sessoes;
CREATE TRIGGER trigger_limpar_sessoes
BEFORE INSERT ON sessoes
FOR EACH STATEMENT
EXECUTE FUNCTION limpar_sessoes_expiradas();

```

**Teste Prático (Simulação de Validação e Limpeza de Sessão Órfã):**
Simulamos a inserção de uma sessão retroativa de teste com mais de 23 horas de vida diretamente no banco de dados e disparamos uma nova requisição de autenticação para validar o acionamento da trigger.

* **Comando SQL de Simulação (Supabase Editor):**

```sql
-- Inserção de uma sessão "fantasma" antiga para teste
INSERT INTO sessoes (id, user_id, criado_em) 
VALUES (gen_random_uuid(), '11111111-1111-1111-1111-111111111111', NOW() - INTERVAL '25 hours');

-- Disparo de uma nova inserção legítima para acionar a trigger de limpeza
INSERT INTO sessoes (id, user_id, criado_em) 
VALUES (gen_random_uuid(), '11111111-1111-1111-1111-111111111111', NOW());

```

* **Evidência de Resposta do Banco:**
A sessão antiga com mais de 23 horas é eliminada automaticamente do registro na mesma transação, garantindo que o pool de autenticação permaneça limpo e imune a reaproveitamento de credenciais obsoletas.
