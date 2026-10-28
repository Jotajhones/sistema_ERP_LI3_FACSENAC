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
