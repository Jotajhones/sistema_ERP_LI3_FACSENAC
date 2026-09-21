import { renderHeader } from "../header/header.js";
import { initListaOrcamentos } from "./listarOrcamento.js";
import { aplicarControleDeAcesso } from "../../scripts/rbac.js";

document.addEventListener("DOMContentLoaded", () => {

    renderHeader('listarOrcamento');
    initListaOrcamentos();
    aplicarControleDeAcesso();
});