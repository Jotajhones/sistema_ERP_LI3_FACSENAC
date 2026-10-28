import { renderHeader } from "../header/header.js";
import { initUser } from "./services/user.js";

window.addEventListener('DOMContentLoaded', () => {
    renderHeader('gestaoPessoas');
    initUser();
});
