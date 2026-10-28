import { renderHeader } from "../../../../rf-002-catalogo-produtos/frontend/header/header.js";
import { initUser } from "./user.js";

window.addEventListener('DOMContentLoaded', () => {
    renderHeader('gestaoPessoas');
    initUser();
});
