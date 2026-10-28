# Backend: Reset Administrativo de Senha (RF-008)

Endpoint protegido para que **GESTOR** e **ADMIN** resetem a senha de um funcionário para o valor padrão, revogando imediatamente todas as sessões ativas dele.

---

## Como Executar Localmente

O módulo é carregado dinamicamente pelo `main.py` do RF-001, então a execução é feita a partir de lá:

```bash
cd ../../rf-001-gestao-identidade/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## Endpoint

| Método | Rota | Perfis | Body |
|---|---|---|---|
| POST | `/usuarios/{user_id}/reset-senha` | ADMIN, GESTOR | nenhum |
| PUT | `/usuarios/minha-senha` | qualquer autenticado | `senha_atual`, `nova_senha` |

`user_id` é o id da tabela `users` (não o de `pessoas`).

Status do reset:

| Status | Quando |
|---|---|
| 200 | Senha resetada e sessões revogadas |
| 401 | Token ausente/inválido |
| 403 | VENDEDOR, ou GESTOR tentando resetar um ADMIN |
| 404 | Usuário não existe |
| 422 | `user_id` não é um UUID |

---

## Regras Implementadas

* **RBAC (OWASP A01):** `Depends(RequireRole(["ADMIN", "GESTOR"]))` barra o VENDEDOR antes de qualquer acesso ao banco. GESTOR também não pode resetar um ADMIN (evita escalada de privilégio).
* **Senha só no servidor (RN-01):** a constante `NOVA_SENHA` fica em `services/reset_senha_service.py`; o frontend não envia senha nenhuma e a resposta não a expõe (RNF-01).
* **Criptografia (OWASP A02):** hash `bcrypt` com 12 rounds antes do `UPDATE users SET password_hash`.
* **Revogação de sessões (OWASP A07):** `resetar_senha_usuario(id, hash_padrao)` em `repositories/reset_senha_repository.py` faz o UPDATE e em seguida `DELETE FROM sessoes WHERE user_id = {id}`.
* **Troca da própria senha (RN-03):** `PUT /usuarios/minha-senha` altera só a senha do dono do token, exigindo a senha atual. Reaproveita a regra de `PUT/PATCH /auth/senha` (RF-001), que continua disponível.
* **Detalhes do funcionário:** `GET /pessoas/{id}` (RF-001) passou a devolver `email` e `role` quando quem consulta é GESTOR/ADMIN; para VENDEDOR esses campos vêm `null`.

---

## Revisão de Segurança (Tech Lead)

* **Limpeza:** os artefatos do fluxo self-service (JWT + e-mail, ADR-028) já tinham sido removidos da pasta `rf-008-auditoria-recuperacao`; foram retirados também o código comentado no `main.py` e as rotas `/recuperar-senha/*`, `/auth/esqueci-senha` e `/auth/redefinir-senha` do `swagger.json`. O rate limiter do login (`dependencies.py`) foi mantido, pois não depende de JWT/e-mail.
* **IDOR (A01):** `AlterarSenhaRequest` usa `extra="forbid"`; qualquer `user_id`/`usuario_id`/`id` no JSON de `PUT /usuarios/minha-senha` ou `PUT/PATCH /auth/senha` é rejeitado com `422`. O alvo da troca vem só do token da sessão.
* **RBAC:** token de VENDEDOR no reset recebe `403` e o hash/sessões do alvo não mudam.

Para repetir os testes via curl (os ataques falham, então é seguro rodar contra o deploy):

```bash
API_URL=https://sistema-erp-li3-facsenac.onrender.com \
TOKEN_VENDEDOR=<token de um VENDEDOR> \
ID_ALVO=<users.id de outro usuário> \
./tests/teste_seguranca_rf008.sh
```
