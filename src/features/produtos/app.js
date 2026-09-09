import { renderHeader } from "../header/header.js";
import { initFormProduto } from "./addProduto.js";

document.addEventListener("DOMContentLoaded", () => {
  
  renderHeader('produtos');
  initFormProduto(); 
});