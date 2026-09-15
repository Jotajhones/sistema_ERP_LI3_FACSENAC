import { initProdutosList } from "./listaProdutos.js";
import { aplicarControleDeAcesso } from "../../scripts/rbac.js"
import { renderHeader } from "../header/header.js";
import { initFormProduto } from "./addProduto.js";

document.addEventListener("DOMContentLoaded", () => {

  renderHeader('produtos');
  initFormProduto();
  initProdutosList();
  aplicarControleDeAcesso();
});