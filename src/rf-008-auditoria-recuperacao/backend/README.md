# Sprint 7: Auditoria, Logs e Recuperação de Acesso (Backend & AppSec)

Este módulo implementa a infraestrutura de backend e proteção cibernética (AppSec) da **Sprint 7** do Sistema ERP Web, atendendo rigorosamente às especificações do **Card #36** do Trello.

---

## 1. Escopo e Objetivos Implementados

1. **Fluxo de "Esqueci minha Senha"**:
   - Geração e validação de tokens JWT temporários (15 minutos de validade) assinados via HMAC-SHA256 (RFC 7519).
   - **Garantia de Uso Único (Single-Use Enforcement)**: O identificador único do token (`jti`) é invalidado imediatamente após a redefinição, impedindo qualquer reutilização.
   - **Revogação de Sessões**: Ao redefinir a credencial, todas as sessões ativas do usuário são revogadas na base de dados para mitigar roubo de conta.
   - **Console Logger do MVP**: No ambiente de homologação/MVP, os tokens e links de redefinição são emitidos diretamente no console da aplicação para teste imediato.

2. **Mitigações de Segurança OWASP AppSec (OWASP A07)**:
   - **Proteção Anti-Enumeração de Contas**: O endpoint de solicitação (`/recuperar-senha/solicitar` e `/auth/esqueci-senha`) retorna respostas com tempo e corpo idênticos independentemente de o e-mail existir ou não na base de dados.
   - **Rate Limiting em Memória (Sliding Window)**:
     - Rota `/auth` (Login): 5 requisições por minuto por IP.
     - Rota `/recuperar-senha/solicitar`: 3 requisições por minuto por IP.
     - Rota `/recuperar-senha/confirmar`: 5 requisições por minuto por IP.
     - Resposta padronizada `HTTP 429 Too Many Requests` com cabeçalho `Retry-After`.

3. **Banco de Dados e Auditoria (DDL)**:
   - Localização: [`database/ddl/sprint-07-auditoria-recuperacao-ddl.sql`](../../../database/ddl/sprint-07-auditoria-recuperacao-ddl.sql)
   - Tabela `recuperacao_tokens`: Persistência de hashes e metadados de auditoria de tokens.
   - Tabelas espelho `audit_produtos` e `audit_os` com Triggers nativas em PostgreSQL para rastrear alterações críticas (`INSERT`, `UPDATE`, `DELETE`).

---

## 2. Endpoints Disponíveis

| Método | Endpoint | Limite Rate Limit | Descrição |
|---|---|---|---|
| `POST` | `/recuperar-senha/solicitar` | 3 req / min | Solicita envio de link/token para redefinição |
| `POST` | `/auth/esqueci-senha` | 3 req / min | Alias de compatibilidade para solicitação |
| `GET`  | `/recuperar-senha/validar` | Livre | Valida o token via query string (`?token=...`) |
| `POST` | `/recuperar-senha/validar` | Livre | Valida o token via body JSON |
| `POST` | `/recuperar-senha/confirmar` | 5 req / min | Redefine a senha com o token de uso único |
| `POST` | `/auth/redefinir-senha` | 5 req / min | Alias de compatibilidade para redefinição |

---

## 3. Exemplos de Uso

### Solicitação (`POST /recuperar-senha/solicitar`)
```json
{
  "email": "vendedor@empresa.com"
}
```

### Validação (`GET /recuperar-senha/validar?token=...`)
Resposta:
```json
{
  "valido": true,
  "mensagem": "Token de recuperação válido e pronto para uso",
  "email_mascarado": "v***r@empresa.com"
}
```

### Redefinição (`POST /recuperar-senha/confirmar`)
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "nova_senha": "NovaSenhaForte123",
  "confirmacao_senha": "NovaSenhaForte123"
}
```
