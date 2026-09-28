import { renderHeader } from "../header/header.js";
import { initMeuPainel } from "./services/meuPainel.js";

window.addEventListener('DOMContentLoaded', () => {
    renderHeader('meuPainel');
    initMeuPainel();
});