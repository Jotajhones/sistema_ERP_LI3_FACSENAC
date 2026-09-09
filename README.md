# Documentação da Branch: `frontend`

## 1. Contexto e Razão de Existir

A branch `frontend` foi criada para resolver definitivamente os problemas estruturais de caminhos e rotas que ocorriam no deploy (tanto na Vercel quanto no GitHub Pages).

Anteriormente, o repositório mantinha uma estrutura mista e fragmentada de monorepo, onde o código de backend, pastas legadas e o frontend ficavam espalhados por subdiretórios profundos (como `src/rf-002-catalogo-produtos/frontend`). Isso causava falhas recorrentes de **Erro 404** em produção, pois os redirecionamentos pós-login (`../../../`) ultrapassavam o escopo da raiz publicada pelos servidores estáticos, embora funcionassem perfeitamente localmente via *Live Server*.

## 2. O Problema Resolvido

* **Caminhos absolutos/relativos quebrados:** Os saltos de pastas (`../../`) quebravam no ambiente de nuvem porque o servidor estático enxerga apenas a pasta raiz configurada para o deploy.
* **Isolamento de ambiente:** Misturar arquivos de backend Python e documentações na mesma árvore publicada de front-end dificultava a configuração de domínios e builds limpos.

## 3. Nova Estrutura Organizada

Nesta branch, a raiz do repositório foi totalmente reestruturada para conter exclusivamente a aplicação frontend modularizada, limpa e padronizada:

```text
.
├── index.html                  <-- Ponto de entrada principal (Tela de Login)
├── README.md                   <-- Documentação da branch
└── src
    ├── features
    │   ├── header              <-- Componente compartilhado de navegação
    │   ├── login               <-- Lógica e controladores de acesso
    │   ├── ordemServico        <-- Listagem, listagem de estoque e operações do catálogo
    │   └── produtos            <-- Formulários de cadastro e validação de itens
    ├── scripts
    │   ├── authInterceptor.js  <-- Interceptor HTTP global para Bearer Token
    │   └── env.js              <-- Configuração de variáveis de ambiente da API
    └── styles
        └── global.css          <-- Estilos globais e variáveis de layout

```

## 4. Vantagens desta Abordagem

1. **Deploy Simplificado:** Tanto na Vercel quanto em outros serviços de hospedagem estática, basta apontar o projeto para a raiz da branch (sem precisar configurar diretórios customizados ou subpastas complexas).
2. **Rotas Limpas:** O uso de caminhos relativos consistentes (`./` e `../`) garante que a navegação entre a tela de login, o catálogo e as ordens de serviço funcione idêntica tanto localmente quanto em produção.
3. **Escalabilidade:** Facilita a adição de novas *features* nas próximas sprints sem quebrar a árvore de arquivos.