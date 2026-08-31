// URL da API de login. Enquanto o back-end não está publicado,
// aponta pro servidor local (rodando com uvicorn na porta 8000).
var URL_API = "http://localhost:8000/auth";

var form = document.getElementById("formLogin");
var campoEmail = document.getElementById("campoEmail");
var campoSenha = document.getElementById("campoSenha");
var inputEmail = document.getElementById("email");
var inputSenha = document.getElementById("senha");
var mensagemEmail = document.getElementById("mensagemEmail");
var mensagemSenha = document.getElementById("mensagemSenha");
var btnEntrar = document.getElementById("btnEntrar");

form.addEventListener("submit", function (evento) {
  evento.preventDefault();

  var valido = validarFormulario();

  if (valido) {
    fazerLogin();
  }
});

function validarFormulario() {
  var email = inputEmail.value.trim();
  var senha = inputSenha.value;
  var formularioValido = true;

  var regexEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (regexEmail.test(email)) {
    campoEmail.className = "campo valido";
    mensagemEmail.textContent = "";
  } else {
    campoEmail.className = "campo invalido";
    mensagemEmail.textContent = "E-mail em formato inválido";
    formularioValido = false;
  }

  if (senha.length > 0) {
    campoSenha.className = "campo valido";
    mensagemSenha.textContent = "";
  } else {
    campoSenha.className = "campo invalido";
    mensagemSenha.textContent = "Senha não pode estar vazia";
    formularioValido = false;
  }

  return formularioValido;
}

function fazerLogin() {
  var email = inputEmail.value.trim();
  var senha = inputSenha.value;

  btnEntrar.className = "btn-entrar carregando";
  btnEntrar.disabled = true;
  btnEntrar.textContent = "Entrando...";

  fetch(URL_API, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      email: email,
      senha: senha
    })
  })
    .then(function (resposta) {
      if (resposta.status === 401) {
        alert("E-mail ou senha incorretos");
        limparCampos();
        return null;
      }

      if (!resposta.ok) {
        alert("Erro ao conectar com o servidor. Tente novamente.");
        return null;
      }

      return resposta.json();
    })
    .then(function (dados) {
      if (dados) {
        alert("Login realizado com sucesso! Perfil: " + dados.role);
        // ainda não existe uma página de painel no projeto;
        // por enquanto só limpa o formulário.
        limparCampos();
      }
    })
    .catch(function () {
      alert("Erro ao conectar com o servidor. Tente novamente.");
    })
    .finally(function () {
      btnEntrar.className = "btn-entrar";
      btnEntrar.disabled = false;
      btnEntrar.textContent = "ENTRAR";
    });
}

function limparCampos() {
  inputEmail.value = "";
  inputSenha.value = "";
  campoEmail.className = "campo";
  campoSenha.className = "campo";
  mensagemEmail.textContent = "";
  mensagemSenha.textContent = "";
}
