import { renderHeader } from "../header/header.js";
import { initDashboard } from "./services/dashboard.js";

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
        window.location.href = '../login/index.html';
        return;
    }

    window.location.href = '../produtos/produtos.html';
}

window.addEventListener('DOMContentLoaded', () => {

    if (!usuarioPodeAcessarDashboard()) {
        redirecionarUsuarioSemPermissao();
        return;
    }

    renderHeader('dashboard');
    initDashboard();
});