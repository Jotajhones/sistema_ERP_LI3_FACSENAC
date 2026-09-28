import { renderHeader } from "../../../../rf-002-catalogo-produtos/frontend/header/header.js";
import { initGestaoPessoas } from "./gestaoPessoas.js";

window.addEventListener('DOMContentLoaded', () => {
    renderHeader('gestaoPessoas');
    initGestaoPessoas();
});