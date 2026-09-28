import { erpFetch } from "../../../../rf-002-catalogo-produtos/frontend/scripts/authInterceptor.js";

export function initGestaoPessoas() {
    const roleUsuario = (localStorage.getItem('userRole') || '').toUpperCase();
    const isGestorOuAdmin = roleUsuario === 'ADMIN' || roleUsuario === 'GESTOR';

    // Elementos da DOM
    const filtroStatus = document.getElementById('filtroStatus');
    const filtroTipo = document.getElementById('filtroTipo');
    const containerFiltroTipo = document.getElementById('containerFiltroTipo');
    const btnNovoFuncionario = document.getElementById('btnNovoFuncionario');
    const tabelaCorpo = document.getElementById('tabelaCorpo');

    const modalFuncionario = document.getElementById('modalFuncionario');
    const formNovoFuncionario = document.getElementById('formNovoFuncionario');
    const btnCancelarModal = document.getElementById('btnCancelarModal');

    // 1. Aplicação do RBAC Visual
    if (isGestorOuAdmin) {
        containerFiltroTipo.style.display = 'flex';
        btnNovoFuncionario.style.display = 'block';
    }

    // 2. Carregamento e Renderização Condicional
    async function carregarTabela() {
        try {
            const ativo = filtroStatus.value;
            let url = '/pessoas';
            if (ativo !== "") {
                url += `?ativo=${ativo}`;
            }

            const respostaFetch = await erpFetch(url);

            let pessoas = await respostaFetch.json();

            if (!Array.isArray(pessoas)) {

                pessoas = pessoas && pessoas.data ? pessoas.data : (pessoas ? [pessoas] : []);
            }

            // 4. Envia o Array limpo para a tabela
            renderizarTabela(pessoas);
        } catch (error) {
            console.error("Erro ao carregar lista:", error);
            alert("Falha ao buscar os dados.");
        }
    }

    function renderizarTabela(pessoas) {
        tabelaCorpo.innerHTML = '';

        const tipoSelecionado = filtroTipo.value;

        // Filtragem visual (Atua apenas para Gestores/Admins, Vendedor sempre terá array só de clientes)
        const pessoasFiltradas = pessoas.filter(p => {
            const isFuncionario = p.user_id !== null;
            if (tipoSelecionado === 'CLIENTE' && isFuncionario) return false;
            if (tipoSelecionado === 'FUNCIONARIO' && !isFuncionario) return false;
            return true;
        });

        pessoasFiltradas.forEach(p => {
            const isFuncionario = p.user_id !== null;
            const contato = isFuncionario ? (p.email || 'N/D') : (p.telefone || 'N/D');
            const classBadgeTipo = isFuncionario ? 'badge-funcionario' : 'badge-cliente';
            const labelTipo = isFuncionario ? 'Funcionário' : 'Cliente';
            const classBadgeAtivo = p.ativo ? 'badge-ativo' : 'badge-inativo';
            const labelAtivo = p.ativo ? 'Ativo' : 'Inativo';

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${p.nome}</td>
                <td>${contato}</td>
                <td><span class="badge ${classBadgeTipo}">${labelTipo}</span></td>
                <td><span class="badge ${classBadgeAtivo}">${labelAtivo}</span></td>
                <td>
                    ${p.ativo
                    ? `<button class="btn-danger btn-inativar" data-id="${p.id}">Excluir</button>`
                    : `<span style="color: #999; font-size: 0.85rem;">Inativado</span>`
                }
                </td>
            `;
            tabelaCorpo.appendChild(tr);
        });

        // Delegação de eventos para os botões de inativação
        document.querySelectorAll('.btn-inativar').forEach(btn => {
            btn.addEventListener('click', (e) => inativarRegistro(e.target.dataset.id));
        });
    }

    // 3. Exclusão (Soft Delete)
    async function inativarRegistro(id) {
        if (!confirm("Atenção (LGPD): Deseja remover o acesso/inativar este cadastro?")) return;

        try {
            await erpFetch(`/pessoas/${id}`, { method: 'DELETE' });
            alert("Cadastro inativado com sucesso.");
            carregarTabela();
        } catch (error) {
            // Intercepta tentativas de escalonamento via manipulação do DOM
            if (error.message && error.message.includes("403")) {
                alert("Acesso Negado: Você não tem permissão para inativar este nível de registro.");
            } else {
                alert(error.message || "Erro ao tentar inativar o registro.");
            }
        }
    }

    // 4. Criação de Funcionário (Restrito)
    if (btnNovoFuncionario) {
        btnNovoFuncionario.addEventListener('click', () => {
            formNovoFuncionario.reset();
            modalFuncionario.style.display = 'flex';
        });
    }

    if (btnCancelarModal) {
        btnCancelarModal.addEventListener('click', () => {
            modalFuncionario.style.display = 'none';
        });
    }

    if (formNovoFuncionario) {
        formNovoFuncionario.addEventListener('submit', async (e) => {
            e.preventDefault();

            const payload = {
                nome: document.getElementById('funcNome').value.trim(),
                email: document.getElementById('funcEmail').value.trim(),
                role: document.getElementById('funcRole').value
            };

            try {
                await erpFetch('/usuarios', {
                    method: 'POST',
                    body: JSON.stringify(payload)
                });

                alert("Funcionário criado com sucesso! Senha padrão gerada.");
                modalFuncionario.style.display = 'none';
                carregarTabela();
            } catch (error) {
                if (error.message && error.message.includes("403")) {
                    alert("Acesso Negado: Apenas Administradores podem criar determinados perfis.");
                } else {
                    alert(error.message || "Erro ao criar funcionário.");
                }
            }
        });
    }


    filtroStatus.addEventListener('change', carregarTabela);
    filtroTipo.addEventListener('change', () => carregarTabela());

    carregarTabela();
}