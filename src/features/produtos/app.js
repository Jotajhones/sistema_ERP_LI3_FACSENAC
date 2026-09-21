import { initProdutosList } from "./services/listaProdutos.js";
import { aplicarControleDeAcesso } from "../../scripts/rbac.js"
import { renderHeader } from "../header/header.js";
import { initFormProduto } from "./services/addProduto.js";

document.addEventListener("DOMContentLoaded", () => {

  renderHeader('produtos');
  initFormProduto();
  initProdutosList();
  aplicarControleDeAcesso();
});