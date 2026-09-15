import { initProdutosList } from "../../../rf-003-gestao-orcamento/frontend/scripts/listaProdutos.js";
import { aplicarControleDeAcesso } from "../../../rf-003-gestao-orcamento/frontend/scripts/rbac.js"
import { renderHeader } from "../header/header.js";
import { initFormProduto } from "./addProduto.js";

document.addEventListener("DOMContentLoaded", () => {

  renderHeader('produtos');
  initFormProduto();
  initProdutosList();
  aplicarControleDeAcesso();
});