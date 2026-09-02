DOCUMENTO DE BACKLOG TÉCNICO E DÍVIDA TÉCNICA (ROADMAP SPRINT 3+)

Este documento centraliza as funcionalidades, melhorias arquiteturais e correções de segurança que foram intencionalmente postergadas nas Sprints 1 e 2 para garantir a entrega do MVP. Deve ser utilizado como guia principal para o planejamento das próximas Sprints.

---

## 1. SEGURANÇA E AUTORIZAÇÃO (BACKEND)

**1.1. Autorização Baseada em Papéis (RBAC) no Backend (AuthZ)**

* **Estado Atual:** O sistema possui Autenticação (AuthN) via token opaco, e o Frontend oculta elementos da UI com base na role. No entanto, a API não valida a permissão. Qualquer usuário com um token válido (incluindo Vendedores) pode disparar um POST para `/produtos` ou `/users` contornando o Frontend.
* **Ação Requerida:** Criar dependências no FastAPI (ex: `RequireRole(['ADMIN', 'GESTOR'])`) para inspecionar a role associada à sessão no banco de dados antes de liberar a execução do endpoint.

**1.2. Rate Limiting e Proteção contra Força Bruta (A07)**

* **Estado Atual:** O endpoint `/auth` não possui limite de tentativas.
* **Ação Requerida:** Implementar limitação de requisições (rate limiting) por IP e bloqueio temporário de conta após múltiplas tentativas falhas.

**1.3. Ajuste de CORS (A05)**

* **Estado Atual:** CORS permissivo (`allow_origins=["*"]`).
* **Ação Requerida:** Restringir as origens aceitas estritamente para o domínio de produção do Frontend (GitHub Pages/Vercel) e localhost.

---

## 2. GESTÃO DE IDENTIDADES (IAM) - FLUXOS PENDENTES

**2.1. Interface de Gestão de Usuários (Frontend)**

* **Estado Atual:** A rota `POST /users` existe no Backend, mas não há interface gráfica para a criação de novos usuários corporativos.
* **Ação Requerida:** Criar tela administrativa no Dashboard para listagem de usuários e cadastro de novas contas (restrito a perfis Admin/Gestor).

**2.2. Fluxo de Redefinição de Senha (Forgot Password)**

* **Estado Atual:** Inexistente. A redefinição manual exigiria intervenção direta no banco de dados.
* **Ação Requerida:** Implementar fluxo seguro de redefinição. Evitar soluções baseadas apenas em CPF (risco de A01 - Broken Access Control). Requisito ideal: geração de token temporário enviado por e-mail ou gerado por um painel administrativo seguro.

**2.3. Correção de Seeds de Desenvolvimento (A02)**

* **Estado Atual:** Os usuários de teste no script `.sql` compartilham o mesmo salt e possuem hashes inválidos em relação à documentação.
* **Ação Requerida:** Regerar os comandos INSERT de usuários utilizando o método `bcrypt` do projeto com salt único para cada registro.

---

## 3. MÓDULO CORE BUSINESS: ORDENS DE SERVIÇO (OS)

**3.1. Arquitetura de Tabelas (DBA)**

* **Estado Atual:** Clientes (`pessoas`) e `produtos` existem de forma isolada.
* **Ação Requerida:** Criar a tabela `ordens_servico` e a tabela associativa `os_produtos` (identificando quantidade, valor unitário no momento da venda e descontos aplicados).

**3.2. Lógica de Descontos e Totalizadores**

* **Estado Atual:** Inexistente.
* **Ação Requerida:** Definir a aplicação de descontos (absolutos ou percentuais) a nível de item e a nível de OS completa, garantindo validação matemática no Backend para evitar manipulação de valores no payload do Frontend.

---

## 4. BANCO DE DADOS E EVENTOS ASSÍNCRONOS (DBA)

**4.1. Triggers de Controle de Estoque**

* **Estado Atual:** A tabela de produtos não possui coluna de quantidade, e não há lógica de baixa.
* **Ação Requerida:** Adicionar controle de estoque em `produtos`. Criar Triggers no PostgreSQL para deduzir o estoque automaticamente após a confirmação (status fechado) de uma Ordem de Serviço, removendo esta responsabilidade da camada de aplicação (Backend).

**4.2. Tabelas de Log de Auditoria Dedicadas**

* **Estado Atual:** O rastreio ocorre através de colunas básicas (`criado_por`, `atualizado_por`) na própria entidade.
* **Ação Requerida:** Para dados críticos e financeiros (OS), criar tabelas espelho de log (ex: `audit_ordens_servico`) alimentadas via Trigger, garantindo o versionamento completo (before/after state) de cada alteração de registro, blindando o histórico contra updates diretos.