import { renderHeader } from "../../../../rf-002-catalogo-produtos/frontend/header/header.js";
import { initDashboard } from "./dashboard.js";

function usuarioPodeAcessarDashboard() {
    const rawRole = localStorage.getItem('userRole');

    const role = rawRole
        ? rawRole.toUpperCase().trim()
        : '';

    return role === 'ADMIN' || role === 'GESTOR';
}

function redirecionarUsuarioSemPermissao() {
    const rawRole = localStorage.getItem('userRole');

    const role = rawRole
        ? rawRole.toUpperCase().trim()
        : '';

    if (!role) {
        window.location.href =
            '../../../../rf-001-gestao-identidade/frontend/login/index.html';
        return;
    }

    window.location.href =
        '../../../../rf-002-catalogo-produtos/frontend/produtos/produtos.html';
}

window.addEventListener('DOMContentLoaded', () => {

    if (!usuarioPodeAcessarDashboard()) {
        redirecionarUsuarioSemPermissao();
        return;
    }

    renderHeader('dashboard');
    initDashboard();
});