# Frontend: Tela de Login (RF-001)

Interface de autenticação do usuário. Desenvolvida em Vanilla JS (HTML5, CSS3, JS) puro, sem frameworks pesados ou bundlers, garantindo alta performance e aderência aos requisitos do projeto.

## Configuração Inicial

O Frontend precisa saber onde a API do Backend está rodando. Como não usamos Node.js aqui, as variáveis são injetadas no objeto `window`.

1. Crie um arquivo chamado `env.js` nesta mesma pasta (`login/`).
2. Adicione o seguinte código para apontar para a sua API local:

```javascript
   window.APP_CONFIG = {
     API_URL: "http://localhost:8000"
   };
```

*(Atenção: O arquivo `env.js` NUNCA deve conter chaves secretas do banco de dados).*

## Como Executar Localmente

Por ser Vanilla JS puro, não há necessidade de rodar processos no terminal.

1. Certifique-se de que o Backend do RF-001 esteja rodando.
2. Abra o arquivo `index.html` diretamente no seu navegador.
* *Dica: Se estiver usando o VS Code, utilize a extensão **Live Server** para facilitar o desenvolvimento e auto-reload.*

## Testes

* O formulário possui validação booleana em tempo real para checar formato de e-mail e campos vazios antes de tentar o envio.
* Se a API estiver offline, um alerta amigável de erro de rede será exibido.