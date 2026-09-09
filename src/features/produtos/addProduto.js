import { erpFetch } from "../../scripts/authInterceptor.js";

let form, inputNome, inputSku, inputValor, inputDescricao, btnSalvar, erroNome, erroValor,btnCancelar;

export function initFormProduto() {
    form = document.getElementById('formProduto');
    inputNome = document.getElementById('nome');
    inputSku = document.getElementById('sku');
    inputValor = document.getElementById('valor_venda');
    inputDescricao = document.getElementById('descricao');
    btnSalvar = document.getElementById('btnSalvar');

    erroNome = document.getElementById('erroNome');
    erroValor = document.getElementById('erroValor');
    btnCancelar = document.getElementById('btnCancelar');

    if (!form) return;

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

    if (btnCancelar) {
        btnCancelar.addEventListener('click', () => {
            window.location.href = '../ordemServico/ordemServico.html';
        });
    }
    
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

    if (!validarFormulario(true)) {
        return;
    }

    const payload = {
        nome: inputNome.value.trim(),
        sku: inputSku.value.trim(),
        valor_venda: parseFloat(inputValor.value),
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
            window.location.href = '../ordemServico/ordemServico.html';
        } else {
            const errorData = await response.json();
            alert(`Erro ao cadastrar: ${errorData.detail || "Verifique os dados e o SKU."}`);
        }
    } catch (error) {
        alert("Erro de conexão. Não foi possível comunicar com o servidor.");
    } finally {
        btnSalvar.disabled = false;
        btnSalvar.textContent = "Salvar Produto";
    }
}