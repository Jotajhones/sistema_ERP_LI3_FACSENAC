import { erpFetch } from "../scripts/authInterceptor.js";
export function renderHeader(activeRoute = 'produtos') {
    const headerContainer = document.getElementById('app-header');

    if (!headerContainer) {
        console.error('Contêiner #app-header não encontrado na página.');
        return;
    }

    const headerHTML = `
        <header class="erp-header">
            <div class="erp-header-brand">
                ERP | SysBuilder
            </div>
            
            <nav class="erp-header-nav">
                <a href="../../frontend/ordemServico/ordemServico.html" class="erp-nav-link ${activeRoute === 'ordemServico' ? 'active' : ''}">
                    Orçamento
                </a>
                <a href="../../frontend/produtos/produtos.html" class="erp-nav-link ${activeRoute === 'produtos' ? 'active' : ''}">
                    Produtos
                </a>
            </nav>

            <div class="erp-header-user">
                <span id="header-user-role" style="font-size: 0.85rem; color: var(--color-border);">
                    Operador
                </span>
                <button id="btn-logout" class="btn-logout">Sair</button>
            </div>
        </header>
    `;

    headerContainer.innerHTML = headerHTML;

    const userRole = localStorage.getItem('userRole');
    if (userRole) {
        document.getElementById('header-user-role').textContent = userRole.toUpperCase();
    }

    document.getElementById('btn-logout').addEventListener('click', async () => {

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