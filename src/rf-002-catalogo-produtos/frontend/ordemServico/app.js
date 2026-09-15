import { initOrcamento } from "../../../rf-003-gestao-orcamento/frontend/scripts/ordemServico.js";
import { aplicarControleDeAcesso } from "../../../rf-003-gestao-orcamento/frontend/scripts/rbac.js";
import { renderHeader } from "../header/header.js";

document.addEventListener("DOMContentLoaded", () => {
    renderHeader('ordemServico');
    initOrcamento();
    aplicarControleDeAcesso();
});