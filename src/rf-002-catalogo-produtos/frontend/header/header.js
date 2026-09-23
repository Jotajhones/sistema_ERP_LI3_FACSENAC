import { erpFetch } from "../scripts/authInterceptor.js";

export function renderHeader(activeRoute = 'produtos') {
    const headerContainer = document.getElementById('app-header');

    if (!headerContainer) {
        console.error('Contêiner #app-header não encontrado na página.');
        return;
    }

    const rawRole = localStorage.getItem('userRole');
    const userRole = rawRole ? rawRole.toUpperCase().trim() : '';
    const isGestorOuAdmin = userRole === 'ADMIN' || userRole === 'GESTOR';
    const displayRole = userRole || 'OPERADOR';

    const headerHTML = `
        <header class="erp-header">
            <div class="erp-header-brand">
                ERP | SysBuilder
            </div>
            
            <nav class="erp-header-nav">
                <a href="../../../rf-002-catalogo-produtos/frontend/ordemServico/ordemServico.html" class="erp-nav-link ${activeRoute === 'ordemServico' ? 'active' : ''}">
                    Novo Orçamento
                </a>
                
                <a href="../../../rf-004-hot-fix-orcamentos-os/frontend/listarOrcamento/listarOrcamento.html" class="erp-nav-link ${activeRoute === 'listarOrcamento' ? 'active' : ''}">
                    Histórico
                </a>

                <a href="../../../rf-002-catalogo-produtos/frontend/produtos/produtos.html" class="erp-nav-link ${activeRoute === 'produtos' ? 'active' : ''}">
                    Produtos
                </a>

                <a href="../../../rf-005-gestao-users/frontend/gestaoPessoas/gestaoPessoas.html" class="erp-nav-link ${activeRoute === 'gestaoPessoas' ? 'active' : ''}">
                    ${isGestorOuAdmin ? 'Pessoas' : 'Clientes'}
                </a>
            </nav>

            <div class="erp-header-user">
                <a href="../../../rf-005-gestao-users/frontend/meuPainel/meuPainel.html" class="erp-nav-link user-profile-link ${activeRoute === 'meuPainel' ? 'active' : ''}">
                    <span id="header-user-role">${displayRole}</span>
                </a>
                <button id="btn-logout" class="btn-logout">Sair</button>
            </div>
        </header>
    `;

    headerContainer.innerHTML = headerHTML;

    const btnLogout = document.getElementById('btn-logout');
    if (btnLogout) {
        btnLogout.addEventListener('click', async () => {
            const token = localStorage.getItem('authToken');
            const controller = new AbortController();
            const timeout = setTimeout(() => controller.abort(), 2000);

            try {
                if (token) {
                    await erpFetch('/auth/logout', {
                        method: 'POST',
                        signal: controller.signal
                    });
                }
            } catch (error) {
                console.error('Erro ao encerrar sessão no servidor:', error);
            } finally {
                clearTimeout(timeout);
                localStorage.removeItem('authToken');
                localStorage.removeItem('userRole');
                window.location.href = '../../../rf-001-gestao-identidade/frontend/login/index.html';
            }
        });
    }
}