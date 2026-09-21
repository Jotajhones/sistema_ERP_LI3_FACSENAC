import { renderHeader } from "../../../rf-002-catalogo-produtos/frontend/header/header.js";
import { initListaOrcamentos } from "./listarOrcamento.js";
import { aplicarControleDeAcesso } from "../../../rf-003-gestao-orcamento/frontend/scripts/rbac.js";

document.addEventListener("DOMContentLoaded", () => {

    renderHeader('listarOrcamento');
    initListaOrcamentos();
    aplicarControleDeAcesso();
});