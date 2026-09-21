import { initOrcamento } from "./services/ordemServico.js";
import { aplicarControleDeAcesso } from "../../scripts/rbac.js";
import { renderHeader } from "../header/header.js";

document.addEventListener("DOMContentLoaded", () => {
    renderHeader('ordemServico');
    initOrcamento();
    aplicarControleDeAcesso();
});