import { erpFetch } from "../../../scripts/authInterceptor.js";

export function initUser() {
    const roleUsuario = (localStorage.getItem('userRole') || '').toUpperCase();
    const isGestorOuAdmin = roleUsuario === 'ADMIN' || roleUsuario === 'GESTOR';

    const idPessoa = new URLSearchParams(window.location.search).get('id');

    // Elementos da DOM
    const alertBox = document.getElementById('feedback-alert');
    const areaResetSenha = document.getElementById('areaResetSenha');
    const btnResetSenha = document.getElementById('btnResetSenha');

    let pessoa = null;

    function exibirAlerta(mensagem, isSucesso = true) {
        alertBox.textContent = mensagem;
        alertBox.className = `alert-message ${isSucesso ? 'alert-success' : 'alert-error'}`;
        alertBox.style.display = 'block';
    }

    // 1. Carregamento do usuário (GET /pessoas/{id})
    async function carregarUsuario() {
        if (!idPessoa) {
            exibirAlerta('Nenhum usuário informado.', false);
            return;
        }

        try {
            const respostaFetch = await erpFetch(`/pessoas/${encodeURIComponent(idPessoa)}`);

            if (respostaFetch.status === 404) {
                exibirAlerta('Usuário não encontrado.', false);
                return;
            }
            if (!respostaFetch.ok) {
                exibirAlerta('Falha ao buscar os dados do usuário.', false);
                return;
            }

            pessoa = await respostaFetch.json();
            if (pessoa && pessoa.data) pessoa = pessoa.data;
            if (Array.isArray(pessoa)) pessoa = pessoa[0];

            renderizarUsuario();
        } catch (error) {
            console.error("Erro ao carregar usuário:", error);
            exibirAlerta('Falha ao buscar os dados do usuário.', false);
        }
    }

    // textContent para não interpretar HTML vindo do banco (XSS)
    function renderizarUsuario() {
        const isFuncionario = pessoa.user_id !== null && pessoa.user_id !== undefined;

        // E-mail e role vêm da tabela users; o GET /pessoas/{id} só os devolve para GESTOR/ADMIN
        const email = pessoa.email;
        const role = (pessoa.role || '').toUpperCase();

        document.getElementById('userNome').textContent = pessoa.nome || 'N/D';
        document.getElementById('userCpf').textContent = formatarCpf(pessoa.cpf);
        document.getElementById('userEmail').textContent = email || 'N/D';

        const badgeTipo = document.getElementById('userTipo');
        badgeTipo.textContent = isFuncionario ? (role || 'Funcionário') : 'Cliente';
        badgeTipo.className = `badge ${isFuncionario ? 'badge-funcionario' : 'badge-cliente'}`;

        const badgeStatus = document.getElementById('userStatus');
        badgeStatus.textContent = pessoa.ativo ? 'Ativo' : 'Inativo';
        badgeStatus.className = `badge ${pessoa.ativo ? 'badge-ativo' : 'badge-inativo'}`;

        // 2. RBAC Visual: reset só para gestor/admin, só em funcionários, e GESTOR não reseta ADMIN
        const gestorVendoAdmin = roleUsuario === 'GESTOR' && role === 'ADMIN';
        if (isGestorOuAdmin && isFuncionario && !gestorVendoAdmin) {
            areaResetSenha.style.display = 'block';
        }
    }

    function formatarCpf(cpf) {
        if (!cpf) return 'N/D';
        const digitos = String(cpf).replace(/\D/g, '');
        if (digitos.length !== 11) return cpf;
        return digitos.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
    }

    // 3. Reset administrativo (POST /usuarios/{id}/reset-senha)
    async function resetarSenha() {
        const confirmado = confirm(
            `Tem certeza que deseja resetar a senha de ${pessoa.nome}? ` +
            `A senha será alterada para 'senha123' e o usuário será deslogado de todas as máquinas.`
        );
        if (!confirmado) return;

        btnResetSenha.disabled = true;

        try {
            // Sem body: a senha padrão é definida exclusivamente no backend (RN-01)
            const respostaFetch = await erpFetch(`/usuarios/${encodeURIComponent(pessoa.user_id)}/reset-senha`, {
                method: 'POST'
            });

            // Permanece na página após o alert
            if (respostaFetch.ok) {
                alert(`Senha de ${pessoa.nome} resetada com sucesso.`);
            } else if (respostaFetch.status === 403) {
                const erro = await respostaFetch.json().catch(() => ({}));
                alert(erro.detail || 'Acesso Negado: apenas Gestores e Administradores podem resetar senhas.');
            } else if (respostaFetch.status === 404) {
                alert('Usuário não encontrado.');
            } else {
                alert('Erro ao resetar a senha. Tente novamente.');
            }
        } catch (error) {
            console.error("Erro ao resetar senha:", error);
            alert('Erro de comunicação com o servidor.');
        } finally {
            btnResetSenha.disabled = false;
        }
    }

    btnResetSenha.addEventListener('click', resetarSenha);

    carregarUsuario();
}
