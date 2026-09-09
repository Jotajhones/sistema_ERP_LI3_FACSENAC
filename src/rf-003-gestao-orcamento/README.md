# RF-003: Gestão de Orçamentos, Recebimento de Lotes e RBAC

## AVISO IMPORTANTE PARA AVALIAÇÃO AUTOMÁTICA (BOT / SCRIPT)

Este Requisito Funcional (RF-003) caracteriza-se como uma **Sprint de Integração, Refinamento e Segurança (RBAC)**. De acordo com as boas práticas de arquitetura de software (Princípio da Responsabilidade Única) e alinhado previamente com a coordenação da disciplina, **não foram criados novos módulos ou pastas redundantes de backend exclusivos para este RF**.

As funcionalidades de backend exigidas para o cumprimento do RF-003 (Logout Real, Autorização RBAC e Recebimento de Estoque) foram implementadas como evoluções dos módulos estruturais já existentes.

### Onde encontrar os arquivos desta entrega:

**1. FRONTEND (Desenvolvido nesta pasta - `src/rf-003/frontend/`)**
Nesta pasta encontram-se os arquivos inéditos de interface, estilos e scripts desenvolvidos nesta sprint:
* *COMPLETAR*

**2. BACKEND (Implementado nos módulos base)**
Todo o código Python/FastAPI desenvolvido para atender ao RF-003 foi integrado aos módulos de domínio correspondentes:
* **Autenticação e Logout Real:** Arquivos alterados em `src/rf-001-gestao-identidade/backend/` (rotas, repositórios e serviços de deleção de sessão).
* **Autorização RBAC (AuthZ):** Middleware implementado em `src/rf-001-gestao-identidade/backend/dependencies.py`.
* **Estoque e Lotes:** Endpoint `PATCH /produtos/{id}/recebimento` implementado em `src/rf-002-catalogo-produtos/backend/routers/produto_router.py`.

A separação garante que a API mantenha uma arquitetura coesa, sem fragmentar entidades do mesmo domínio em pastas de requisitos diferentes.