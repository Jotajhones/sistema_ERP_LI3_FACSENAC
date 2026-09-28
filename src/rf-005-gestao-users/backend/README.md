# Backend: Gestão de Contas, Credenciais e RBAC (RF-005)

API REST desenvolvida em **FastAPI (Python)** e integrada ao PostgreSQL/Supabase, responsável pelo gerenciamento de identidade, provisionamento seguro de contas de colaboradores e governança de permissões (Role-Based Access Control - RBAC).

---

## O Motivo deste Módulo

O RF-005 desacopla a camada de autenticação base da gestão administrativa de usuários corporativos. Ele centraliza o provisionamento restrito de acessos para funcionários (`VENDEDOR` e `GESTOR`), delega permissões conforme o princípio do menor privilégio e atua em conformidade com as diretrizes de privacidade (LGPD), assegurando que credenciais de colaboradores sejam geradas sob regras rígidas de segurança sem expor perfis sensíveis.

---

## Como Executar Localmente

A arquitetura do ERP utiliza um carregador dinâmico central (`importlib`) para compor os microsserviços. Por isso, **a execução deve ser feita obrigatoriamente a partir da pasta raiz do RF-001**.

1. Navegue até a pasta do motor base:

```bash
cd ../../rf-001-gestao-identidade/backend

```

2. Certifique-se de que o ambiente virtual está ativo (`source venv/bin/activate`) e as variáveis no `.env` estão configuradas.
3. Inicie o servidor de desenvolvimento:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000

```

---

## Arquitetura e Regras de Negócio Principais

* **Segregação de Entidades (`users` vs `pessoas`):**
* `users`: Armazena unicamente os metadados de autenticação (`email`, `password_hash`, `user_role`, `ativo`).
* `pessoas`: Guarda os dados cadastrais (`nome`, `cpf`, `telefone`, `user_id`). A chave estrangeira `user_id` vincula o colaborador à sua conta de acesso, enquanto clientes de balcão mantêm `user_id` nulo.


* **Provisionamento Seguro de Credenciais:**
* Endpoint `POST /usuarios`: Exclusivo para perfis `ADMIN` e `GESTOR`.
* Criação automática com senha inicial padrão criptografada via **Bcrypt** com `salt` de 12 rounds (`senha123`), eliminando a necessidade de transmissão de senhas em texto puro pelo formulário de criação.
* Validação de unicidade de e-mail com resposta imediata `409 Conflict` em caso de duplicidade.


* **Governança RBAC Estrita (Controle de Acesso Quebrado - OWASP A01):**
* **VENDEDOR:** Acesso estritamente bloqueado para rotas de criação e listagem de colaboradores (`403 Forbidden`). Só interage com registros de clientes de balcão (`user_id IS NULL`).
* **GESTOR / ADMIN:** Acesso total à listagem, alternância entre visualização de colaboradores e clientes, e criação de novas contas.


* **Conformidade LGPD via Soft Delete:**
* A inativação de cadastros (`DELETE /pessoas/{id}`) nunca remove linhas fisicamente do banco de dados (sem `DROP`/`DELETE` em cascata), preservando a integridade referencial com vendas históricas e ordens de serviço.
* O registro é marcado com `ativo = false`, revogando acessos em tempo de execução sem corromper a rastreabilidade fiscal.