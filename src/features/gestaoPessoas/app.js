import { renderHeader } from "../header/header.js";
import { initGestaoPessoas } from "./services/gestaoPessoas.js";

window.addEventListener('DOMContentLoaded', () => {
    renderHeader('gestaoPessoas');
    initGestaoPessoas();
});