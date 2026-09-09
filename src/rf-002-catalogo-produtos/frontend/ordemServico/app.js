import { initDashboard } from "./ordemServico.js";
import { renderHeader } from "../header/header.js";

document.addEventListener("DOMContentLoaded", () => {
    renderHeader('ordemServico');
    initDashboard();

    const btnNovo = document.getElementById('btnNovoProduto');
    if (btnNovo) {
        btnNovo.addEventListener('click', () => {
            window.location.href = '../produtos/produtos.html';
        });
    }
});