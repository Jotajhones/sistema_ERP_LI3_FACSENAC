import { erpFetch } from "../scripts/authInterceptor.js";

let modalAdd, btnAbrirModalAdd, btnCancelarAdd;
let form, inputNome, inputSku, inputValor, inputUnidade, inputQuantidade, inputDescricao, btnSalvar, erroNome, erroValor;

export function initFormProduto() {
    modalAdd = document.getElementById('modalAddProduto');
    btnAbrirModalAdd = document.getElementById('btnAbrirModalAdd');
    btnCancelarAdd = document.getElementById('btnCancelarAdd');
    
    form = document.getElementById('formProduto');
    inputNome = document.getElementById('nome');
    inputSku = document.getElementById('sku');
    inputValor = document.getElementById('valor_venda');
    inputUnidade = document.getElementById('unidade_medida');
    inputQuantidade = document.getElementById('quantidade_estoque');
    inputDescricao = document.getElementById('descricao');
    btnSalvar = document.getElementById('btnSalvar');

    erroNome = document.getElementById('erroNome');
    erroValor = document.getElementById('erroValor');

    if (!form) return;

    btnAbrirModalAdd.addEventListener('click', () => {
        modalAdd.style.display = 'flex';
    });

    btnCancelarAdd.addEventListener('click', () => {
        modalAdd.style.display = 'none';
        form.reset();
        validarFormulario(false);
    });

    inputNome.addEventListener('input', () => validarFormulario(false));
    inputValor.addEventListener('input', () => validarFormulario(false));
    inputSku.addEventListener('input', () => validarFormulario(false));

    inputNome.addEventListener('blur', () => {
        if (inputNome.value.trim().length === 0) erroNome.style.display = 'block';
    });

    inputValor.addEventListener('blur', () => {
        const valor = parseFloat(inputValor.value);
        if (isNaN(valor) || valor < 0) erroValor.style.display = 'block';
    });

    form.addEventListener('submit', addProduto);
}

export function validarFormulario(mostrarErros = false) {
    const isNomeValido = inputNome.value.trim().length > 0;
    const valor = parseFloat(inputValor.value);
    const isValorValido = !isNaN(valor) && valor >= 0;
    const isSkuValido = inputSku.value.trim().length > 0;

    if (mostrarErros) {
        erroNome.style.display = isNomeValido ? 'none' : 'block';
        erroValor.style.display = isValorValido ? 'none' : 'block';
    } else {
        if (isNomeValido) erroNome.style.display = 'none';
        if (isValorValido) erroValor.style.display = 'none';
    }

    const formValido = isNomeValido && isValorValido && isSkuValido;
    btnSalvar.disabled = !formValido;

    return formValido;
}

export async function addProduto(e) {
    e.preventDefault();

    if (!validarFormulario(true)) return;

    const payload = {
        nome: inputNome.value.trim(),
        sku: inputSku.value.trim(),
        valor_venda: parseFloat(inputValor.value),
        unidade_medida: inputUnidade.value,
        quantidade_estoque: parseInt(inputQuantidade.value) || 0, 
        descricao: inputDescricao.value.trim() || null
    };

    btnSalvar.disabled = true;
    btnSalvar.textContent = "Salvando...";

    try {
        const response = await erpFetch('/produtos', {
            method: 'POST',
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            alert("Produto cadastrado com sucesso!");
            form.reset();
            window.location.reload(); 
        } else {
            const errorData = await response.json();
            alert(`Erro ao cadastrar: ${errorData.detail || "Verifique os dados."}`);
        }
    } catch (error) {
        alert("Erro de conexão. Não foi possível comunicar com o servidor.");
    } finally {
        btnSalvar.disabled = false;
        btnSalvar.textContent = "Salvar Produto";
    }
}