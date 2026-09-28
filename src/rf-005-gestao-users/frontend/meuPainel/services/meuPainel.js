import { erpFetch } from "../../../../rf-002-catalogo-produtos/frontend/scripts/authInterceptor.js";

export function initMeuPainel() {
    const formMeuPainel = document.getElementById('formMeuPainel');
    const formTrocaSenha = document.getElementById('formTrocaSenha');
    const modalSenha = document.getElementById('modalSenha');
    const btnAbrirModalSenha = document.getElementById('btnAbrirModalSenha');
    const btnCancelarSenha = document.getElementById('btnCancelarSenha');
    const alertBox = document.getElementById('feedback-alert');
    const modalFeedback = document.getElementById('modal-feedback');

    function exibirAlerta(mensagem, isSucesso = true) {
        if (!alertBox) return;
        alertBox.textContent = mensagem;
        alertBox.className = `alert-message ${isSucesso ? 'alert-success' : 'alert-error'}`;
        alertBox.style.display = 'block';
        setTimeout(() => {
            alertBox.style.display = 'none';
        }, 5000);
    }

    function exibirFeedbackModal(mensagem, isSucesso = false) {
        if (!modalFeedback) return;
        modalFeedback.textContent = mensagem;
        modalFeedback.style.color = isSucesso ? 'var(--color-success)' : 'var(--color-error)';
    }

    let idPessoaLogada = localStorage.getItem('pessoaId') || localStorage.getItem('userId');

    async function carregarDadosUsuario() {
        const roleSalva = localStorage.getItem('userRole') || 'OPERADOR';
        document.getElementById('userRoleInput').value = roleSalva;

        try {
            let respostaFetch = null;

            if (idPessoaLogada) {
                try {
                    respostaFetch = await erpFetch(`/pessoas/${idPessoaLogada}`);
                } catch (e) {
                    console.warn('Não foi possível carregar pessoa pelo ID salvo:', e);
                }
            }

            if (!respostaFetch) {
                throw new Error("Não foi possível carregar os dados cadastrais da sua conta.");
            }


            let pessoa = await respostaFetch.json();

            if (typeof pessoa === 'string') {
                try { pessoa = JSON.parse(pessoa); } catch (e) { }
            }

            if (pessoa && pessoa.data) {
                pessoa = pessoa.data;
            }

            if (Array.isArray(pessoa)) {
                pessoa = pessoa[0];
            }

            if (pessoa && pessoa.id) {
                idPessoaLogada = pessoa.id;
                localStorage.setItem('pessoaId', pessoa.id);
            }

            // Preenche o formulário
            const inputNome = document.getElementById('nomeInput');
            const inputTelefone = document.getElementById('telefoneInput');
            const inputEmail = document.getElementById('userEmailInput');

            if (inputNome) inputNome.value = pessoa.nome || '';
            if (inputTelefone) inputTelefone.value = pessoa.telefone || '';
            if (inputEmail) inputEmail.value = localStorage.getItem('userEmail') || '';

            console.log("3. Campos preenchidos no HTML!");

        } catch (error) {
            console.error('Erro ao carregar dados do usuário:', error);
            exibirAlerta('Aviso ao carregar dados do perfil. Você ainda pode alterar sua senha.', false);
        }
    }

    if (formMeuPainel) {
        formMeuPainel.addEventListener('submit', async (e) => {
            e.preventDefault();

            const nome = document.getElementById('nomeInput').value.trim();
            const telefone = document.getElementById('telefoneInput').value.trim();

            if (!nome) {
                exibirAlerta('O campo Nome é obrigatório.', false);
                return;
            }

            if (!idPessoaLogada) {
                exibirAlerta('Aviso: ID de pessoa não vinculado ao usuário logado.', false);
                return;
            }

            try {
                await erpFetch(`/pessoas/${idPessoaLogada}`, {
                    method: 'PUT',
                    body: JSON.stringify({
                        nome: nome,
                        telefone: telefone
                    })
                });

                exibirAlerta('Dados atualizados com sucesso!', true);
            } catch (error) {
                console.error('Erro ao atualizar dados:', error);
                exibirAlerta(error.message || 'Falha ao atualizar dados.', false);
            }
        });
    }

    if (btnAbrirModalSenha) {
        btnAbrirModalSenha.addEventListener('click', () => {
            formTrocaSenha.reset();
            modalFeedback.textContent = '';
            modalSenha.style.display = 'flex';
        });
    }

    if (btnCancelarSenha) {
        btnCancelarSenha.addEventListener('click', () => {
            modalSenha.style.display = 'none';
        });
    }

    if (formTrocaSenha) {
        formTrocaSenha.addEventListener('submit', async (e) => {
            e.preventDefault();
            modalFeedback.textContent = '';

            const senhaAtual = document.getElementById('senhaAtual').value;
            const novaSenha = document.getElementById('novaSenha').value;
            const confirmarNovaSenha = document.getElementById('confirmarNovaSenha').value;

            // Validação no JS
            if (novaSenha !== confirmarNovaSenha) {
                exibirFeedbackModal('A nova senha e a confirmação não coincidem.');
                return;
            }

            if (novaSenha.length < 6) {
                exibirFeedbackModal('A nova senha deve ter no mínimo 6 caracteres.');
                return;
            }

            // Payload blindado: apenas senha_atual e nova_senha
            const payload = {
                senha_atual: senhaAtual,
                nova_senha: novaSenha
            };

            try {
                await erpFetch('/auth/senha', {
                    method: 'PATCH',
                    body: JSON.stringify(payload)
                });

                modalSenha.style.display = 'none';
                exibirAlerta('Senha alterada com sucesso!', true);
            } catch (error) {
                console.error('Erro ao alterar senha:', error);
                exibirFeedbackModal(error.message || 'Erro ao alterar senha.');
            }
        });
    }

    carregarDadosUsuario();
}