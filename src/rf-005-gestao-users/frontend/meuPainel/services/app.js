import { renderHeader } from "../../../../rf-002-catalogo-produtos/frontend/header/header.js";
import { initMeuPainel } from "./meuPainel.js";

window.addEventListener('DOMContentLoaded', () => {
    renderHeader('meuPainel');
    initMeuPainel();
});