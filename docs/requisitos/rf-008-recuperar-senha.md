# DOCUMENTO DE ESPECIFICAÇÃO DE REQUISITOS E ARQUITETURA SEGURA (SSD)
Laboratório de Inovação III — Prof. Edilberto Silva — 2026
VERSÃO 16.3 — COM VALIDAÇÃO AGNÓSTICA DE LINGUAGEM

## 1. METADADOS DO PROJETO E DA EQUIPE

### 1.1 Identificação
NOME_DO_PROJETO: Sistema ERP Construção  
DESCRICAO_BREVE: Módulo de reset de credenciais com invalidação de sessões ativas para retomada de acesso operacional rápido na loja física.

### 1.2 Localização dos Artefatos (URLs Obrigatórias)
LINK_REPOSITORIO_GITHUB: https://github.com/Jotajhones/sistema_ERP_LI3_FACSENAC
LINK_APLICACAO_DEPLOY: https://sistema-erp-li3-facsenac.onrender.com/
LINK_BANCO_DADOS: https://supabase.com/dashboard/project/qlfjdnljfmicjkrbrwih/editor/
LINK_DEMONSTRAÇÃO: https://sistema-erp-li-3-facsenac.vercel.app/

### 1.3 Composição da Equipe
| ID | Nome Completo | Papel Primário | Papel Secundário | E-mail / Contato |
|---|---|---|---|---|
| 1 | João Pedro de Lima | Product Owner | Tech Lead / DevOps | joao52517876@edu.df.senac.br |
| 2 | Miguel Nunes | Desenvolvedor Back-End | Full Stack | miguel59970766@edu.df.senac.br |
| 3 | Luciano Santos | Desenvolvedor Back-End | Full Stack  | luciano58995256@edu.df.senac.br |
| 4 | Daniel Silva | DBA / Banco de Dados | Full Stack  | daniel52370026@edu.df.senac.br |
| 5 | Arthur Andrade | Desenvolvedor Front-End | Full Stack  | arthur59275206@edu.df.senac.br |
| 6 | Pedro Soares| Desenvolvedor Front-End | Full Stack  | pedro59153296@edu.df.senac.br |
| 7 | Matheus Chagas | AppSec / QA | Full Stack | matheus57119256@edu.df.senac.br |

---

# RF-008: Recuperação de Senha (Reset Administrativo)

## 1. Identificação

- **ID:** RF-008  
- **Título:** Recuperação de Senha e Invalidação de Sessão  
- **Prioridade:** Alta  
- **Complexidade:** 3 story points  
- **Status:** CONCLUÍDO  

### a) URL da Aplicação (Deploy Online)
- **URL:** https://sistema-erp-li-3-facsenac.vercel.app/  
- **Plataforma:** Vercel  
- **Acesso:** Público  

### b) Link do Banco de Dados Online
- **BD:** Supabase (PostgreSQL)  
- **Link:** https://supabase.com/dashboard/project/qlfjdnljfmicjkrbrwih/editor/  
- **Acesso:** Leitura para o professor (email: prof.edilberto.silva@gmail.com)
- **Tabela principal:** users (coluna password_hash) / sessoes  

### c) Link do GitHub (Repositório)
- **Repositório:** https://github.com/Jotajhones/sistema_ERP_LI3_FACSENAC  
- **Branch principal:** main   
- **Estrutura:** Conforme guia (docs/, src/, database/)  

---

## 2. Descrição e Atores

O requisito de Recuperação de Senha resolve o bloqueio operacional causado pelo esquecimento de credenciais na rotina dinâmica de uma loja física de materiais de construção. Ao invés de depender de envios de e-mail e geração de tokens temporários via internet, o fluxo adota um modelo estritamente administrativo.

O Gestor da unidade utiliza seu painel de controle corporativo para auditar o perfil do funcionário e acionar um reset manual. O sistema automaticamente força uma senha padrão, criptografa o dado e destrói imediatamente todas as sessões ativas (UUID) do funcionário no banco de dados. O operador então loga com a senha de recuperação e realiza a personalização de sua credencial em seu painel privado.

### Benefícios para o Negócio
- Retomada instantânea da operação no caixa sem dependência de plataformas externas de e-mail (SMTP).
- Eliminação de risco de invasão por sessões presas, graças ao deslogamento forçado instantâneo.
- Redução na complexidade técnica da aplicação, eliminando a manutenção de fluxos expirados e gerenciadores de cache paralelo.

### Atores

#### Gestor / Admin (Ator Principal)
- **Papel:** Gestor responsável por destravar o acesso da equipe comercial.  
- **Permissões:** Update (Acionar a rota de reset para reescrever o hash e apagar a sessão alvo).  
- **Acesso:** Tela detalhada do usuário na Gestão de Pessoas.  

#### Vendedor (Ator Secundário)
- **Papel:** Operador de caixa.  
- **Permissões:** Update (Alterar a própria senha padrão no Meu Painel após o reset).  
- **Acesso:** Restrito ao próprio painel corporativo (meuPainel).  

#### Sistema (Automático)
- **Papel:** Validador e Executor Criptográfico.  
- **Permissões:** Validar o controle de acesso (RBAC), gerar o hash nativamente no backend e executar a deleção de instâncias na tabela de sessões.  

---

## 3. Casos de Uso e Requisitos Não-Funcionais

### Fluxo Principal: Reset Administrativo de Credenciais

**Pré-condições:**
- Usuário autenticado possuindo o perfil GESTOR ou ADMIN.  
- O ID do funcionário alvo deve existir na tabela de usuários.  

**Fluxo:**
1. Gestor acessa a tela de "Gestão de Pessoas" e clica no card de um funcionário.  
2. Sistema (Frontend) abre a página de detalhes do usuário (user.html).  
3. Sistema carrega as informações do funcionário e exibe o botão "Resetar Senha para Padrão".  
4. Gestor clica no botão de reset.  
5. Sistema (Frontend) exibe uma caixa de diálogo nativa alertando sobre o deslogamento global do usuário e a aplicação da senha padrão.  
6. Gestor confirma a operação.  
7. Sistema (Frontend) dispara a requisição POST `/usuarios/{id}/reset-senha`.  
8. Sistema (Backend) intercepta e confirma via middleware se a requisição partiu de um gestor autorizado.  
9. Sistema (Backend) define internamente o texto da nova senha e executa a criptografia bcrypt 12 rounds em memória.  
10. Sistema (Backend) atualiza a coluna `password_hash` daquele usuário.  
11. Sistema (Backend) executa `DELETE FROM sessoes WHERE user_id = {id}` para matar conexões presas.  
12. Sistema (Frontend) recebe HTTP 200 OK e notifica o gestor sobre o sucesso do reset.  

**Pós-condições:**
- Hash da senha do funcionário substituído de forma irrecuperável.  
- Funcionário ejetado forçadamente de todas as máquinas logadas.  

### Fluxos Alternativos

**Fluxo Alternativo A1: Bypass de Perfil por Vendedor**
1. No passo 7, um vendedor inspeciona a rede e tenta acionar a rota de reset para outro colega ou gerente enviando o POST diretamente.  
2. O Backend executa o validador RBAC `RequireRole(["ADMIN", "GESTOR"])`.  
3. A autorização falha e a API rejeita o tráfego respondendo `403 Forbidden`.  
4. O hash do gerente permanece intacto.  

**Fluxo Alternativo A2: Personalização da Senha pelo Funcionário**
1. O funcionário que sofreu o reset realiza login com a senha padrão informada pelo Gestor.
2. O funcionário acessa o menu "Meu Painel".  
3. O funcionário preenche a senha padrão e cadastra uma nova senha exclusiva.  
4. O Backend confirma a validade da senha antiga e atualiza o hash, retomando o sigilo corporativo.  

### Regras de Negócio

- **RN-01:** Hash Exclusivo Server-Side: O payload do frontend jamais deve enviar qual será a senha padrão no corpo da requisição. O valor a ser hasteado deve residir em variável constante isolada no Python para evitar adulteração na requisição.  
- **RN-02:** Revogação Compulsória: Todo reset de senha aciona compulsoriamente a quebra da integridade de sessão na tabela respectiva para garantir proteção de contas.  
- **RN-03:** Restrição de Rotas de Mutações Alheias: Somente níveis gerenciais podem realizar reset em IDs arbitrários. O usuário base só tem permissão para alterar a própria credencial vinculada ao token atual. 

### Requisitos Não-Funcionais

- **RNF-01:** Segurança de Acesso: O endpoint de reset não deve expor a senha gerada na resposta JSON, retornando apenas status de confirmação lógica.
- **RNF-02:** Usabilidade Limpa: A função `confirm()` nativa do Javascript deve ser utilizada para travar cliques acidentais no botão de reset.

---

## 4. Protótipo Funcional e Integração de API

> **AVISO DE SEGURANÇA E PROTEÇÃO GLOBAL DE ROTAS (A01:2021)**
>
> Faz-se necessário explicitar que **absolutamente todas as rotas do backend desta aplicação** são rigorosamente protegidas pelo motor de identidade consolidado no MVP. 
>
> Uma simples requisição GET/POST direta aos endpoints via navegador ou curl, sem o contexto de autenticação, resultará em bloqueio liminar (`401 Unauthorized` ou `403 Forbidden`). **Isso não configura falha na API, mas sim o pleno e correto funcionamento do controle de acesso.**
>
> A aplicação utiliza tokens de Sessão Opaca (UUID) gerados localmente pela própria infraestrutura. Caso o avaliador necessite de mocks detalhados para testar o bypass, as instruções estão centralizadas na documentação de fundação de segurança: `/docs/requisitos/RF-001-gestao-identidade.md`.

**Operações Implementadas (Módulo de Identidade Restrita):**

| Operação | Método | Endpoint | Status Esperado |
|---|---|---|---|
| Update | POST | /api/usuarios/{id}/reset-senha | 200 OK |
| Update | PUT | /api/usuarios/minha-senha | 200 OK |
| Read | GET | /api/pessoas/{id} | 200 OK |

**Documentação Obrigatória da API:**
O arquivo técnico OpenAPI refletindo rigorosamente o comportamento testado das rotas está localizado em:
`docs/api/swagger.json`

---

## 5. Arquitetura e Decisões

### Componentes da Arquitetura
- **Frontend:** Manipulação do DOM (Vanilla JS) com chamadas fetch isoladas interceptando a renderização de alertas e modais nativos.
- **Backend:** Python/FastAPI validando contextos e injetando diretrizes fixas no Supabase Client.
- **Banco de Dados:** Tabela de identificadores (`users`), metadados corporativos (`pessoas`) e camada volátil (`sessoes`).

### Decisões Técnicas (ADRs)

**ADR-028: Rejeição de Recuperação de Senha Self-Service (via E-mail e JWT)**
- **Razão:** A proposta de recuperação autônoma exigiria integração com servidores SMTP, geração paralela de tokens JWT e jobs de expiração de banco. Para um MVP de balcão de vendas de construção civil, essa infraestrutura adiciona pontos críticos de falha de rede sem justificar o ROI operacional.
- **Consequências:** Escopo enxuto protegido contra *Feature Creep*. A complexidade despenca, assim como os riscos de vulnerabilidades por má gestão de caches expirados.

**ADR-029: Fluxo de Reset Administrativo Padrão e Invalidação de Sessão**
- **Razão:** Funcionários de caixa precisam de suporte imediato presencial para não travar filas. Movendo o controle para o gerente logado, o suporte leva poucos segundos.
- **Consequências:** A adição de um comando mandatório de `DELETE` contra a tabela de sessões mitiga instantaneamente sequestros de credencial, unindo suporte técnico e governança cibernética.

---

## 6. Segurança OWASP

### Controle 1: Insecure Direct Object Reference (Broken Access Control) - A01:2021

**Vulnerabilidade OWASP (Risco):**
Um funcionário mal-intencionado da ponta poderia montar um script para atacar o backend, enviando IDs de gestores ou outros colegas para a rota `/usuarios/{id}/reset-senha`, derrubando as sessões da liderança e forçando senhas genéricas.

**Implementação (Como você protege?):**
A rota foi construída em FastAPI com o decorador atrelado ao AuthZ de gestão `Depends(RequireRole(["ADMIN", "GESTOR"]))`. Quando o token recebido pertence à role `VENDEDOR`, o Framework não chega sequer a processar o parâmetro do ID na URL, abortando a função no nascedouro.

**Teste (Como provou que funciona?):**
Disparo de uma requisição REST via CURL simulando o uso de um token válido pertencente a um caixa. O sistema devolveu código HTTP 403 Forbidden. A tabela de auditoria provou que o hash do ID alvo não sofreu reescrita e as sessões permaneceram abertas.

### Controle 2: Cryptographic Failures - A02:2021

**Vulnerabilidade OWASP (Risco):**
A definição de uma senha padrão ("senha123") por vias administrativas não isenta a necessidade de armazenamento seguro. O salvamento desta string em texto limpo comprometeria todo o banco de dados em um potencial vazamento.

**Implementação (Como você protege?):**
O módulo de Reset nunca envia senhas pela rede e não insere *plain-texts* no banco. O servidor Python armazena o padrão em uma variável constante de ambiente protegido, aplicando o salt estocástico com `bcrypt` (fator 12 de custo) antes da Query de UPDATE ser submetida.

**Teste (Como provou que funciona?):**
Auditoria manual na interface do Supabase após o Reset. O campo `password_hash` constava como `$2b$12$exemploDeHashIlegivelNoBanco...`, garantindo que um administrador do banco ou invasor logado jamais saberia prever a senha em texto legível.

### Controle 3: Identification and Authentication Failures - A07:2021

**Vulnerabilidade OWASP (Risco):**
Sessões zumbis (Tokens UUID ativos salvos em cache ou em computadores sem supervisão) permitiriam que antigos operadores ou invasores que tivessem furtado as credenciais originais continuassem acessando o painel indefinidamente, mesmo após o administrador resetar a senha.

**Implementação (Como você protege?):**
O método no Python Repository acopla compulsoriamente a operação de UPDATE na tabela `users` com uma operação de deleção na tabela de sessões (`DELETE FROM sessoes WHERE user_id = id_alvo`). As operações formam uma política atrelada.

**Teste (Como provou que funciona?):**
Logado como Vendedor na Janela A, e como Gestor na Janela B. O Gestor apertou o Reset de Senha do Vendedor. Na sequência, a Janela A do vendedor tentou dar refresh na página de clientes. A API validou a perda do registro UUID no Supabase, invalidou o acesso, devolveu 401 Unauthorized e o Vendedor foi lançado de volta à tela inicial de Login.
