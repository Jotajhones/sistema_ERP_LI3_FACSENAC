
document.addEventListener("DOMContentLoaded", () => {

  const API_URL = `${window.APP_CONFIG.API_URL}/auth`;

  const formLogin = document.getElementById("formLogin");
  const containerEmail = document.getElementById("campoEmail");
  const containerSenha = document.getElementById("campoSenha");
  const inputEmail = document.getElementById("email");
  const inputSenha = document.getElementById("senha");
  const msgEmail = document.getElementById("mensagemEmail");
  const msgSenha = document.getElementById("mensagemSenha");
  const btnEntrar = document.getElementById("btnEntrar");


  formLogin.addEventListener("submit", async (evento) => {
    evento.preventDefault();

    const isFormValid = validarFormulario();

    if (isFormValid) {
      await fazerLogin();
    }
  });

  function validarFormulario() {
    const email = inputEmail.value.trim();
    const senha = inputSenha.value;
    let formularioValido = true;

    const regexEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (regexEmail.test(email)) {
      containerEmail.className = "campo valido";
      msgEmail.textContent = "";
    } else {
      containerEmail.className = "campo invalido";
      msgEmail.textContent = "E-mail em formato inválido";
      formularioValido = false;
    }

    if (senha.length > 0) {
      containerSenha.className = "campo valido";
      msgSenha.textContent = "";
    } else {
      containerSenha.className = "campo invalido";
      msgSenha.textContent = "Senha não pode estar vazia";
      formularioValido = false;
    }

    return formularioValido;
  }


  async function fazerLogin() {
    const email = inputEmail.value.trim();
    const senha = inputSenha.value;


    btnEntrar.className = "btn-entrar carregando";
    btnEntrar.disabled = true;
    btnEntrar.textContent = "Entrando...";

    try {
      const resposta = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ email, senha })
      });

      if (resposta.status === 401) {
        alert("E-mail ou senha incorretos");
        limparCampos();
        return;
      }

      if (!resposta.ok) {
        alert("Erro ao conectar com o servidor. Tente novamente.");
        return;
      }

      const dados = await resposta.json();
      alert(`Login realizado com sucesso! Perfil: ${dados.role}`); // Template literals
      limparCampos();

    } catch (erro) {
      alert("Erro de rede ao conectar com o servidor. Tente novamente.");
    } finally {

      btnEntrar.className = "btn-entrar";
      btnEntrar.disabled = false;
      btnEntrar.textContent = "ENTRAR";
    }
  }

  function limparCampos() {
    inputEmail.value = "";
    inputSenha.value = "";
    containerEmail.className = "campo";
    containerSenha.className = "campo";
    msgEmail.textContent = "";
    msgSenha.textContent = "";
  }
});