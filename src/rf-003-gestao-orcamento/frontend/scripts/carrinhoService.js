let carrinho = [];

export function getCarrinho() {
    return carrinho;
}

export function setCarrinho(novoCarrinho) {
    carrinho = novoCarrinho;
}

export function formatarMoeda(valor) {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(valor);
}

export function adicionarAoCarrinho(produto) {
    const existente = carrinho.find(item => item.id === produto.id);
    if (existente) {
        existente.quantidade += 1;
    } else {
        carrinho.push({
            id: produto.id,
            nome: produto.nome,
            valor_venda: produto.valor_venda,
            quantidade: 1
        });
    }
    
    document.getElementById('inputBuscaProduto').value = '';
    document.getElementById('dropdownResultados').style.display = 'none';
    renderizarCarrinho();
}

export function renderizarCarrinho() {
    const tbody = document.getElementById('carrinhoBody');
    const totalEl = document.getElementById('totalOrcamento');
    let total = 0;

    tbody.innerHTML = '';

    if (carrinho.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center" style="padding: 2rem; color: var(--color-text-muted);">Nenhum produto adicionado.</td></tr>';
        totalEl.textContent = 'R$ 0,00';
        return;
    }

    carrinho.forEach((item, index) => {
        const subtotal = item.quantidade * item.valor_venda;
        total += subtotal;

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${item.nome}</td>
            <td class="text-center">
                <input type="number" min="1" class="input-qtd" value="${item.quantidade}" data-index="${index}">
            </td>
            <td class="text-right">${formatarMoeda(item.valor_venda)}</td>
            <td class="text-right" style="font-weight: 500;">${formatarMoeda(subtotal)}</td>
            <td class="text-center">
                <button type="button" class="btn-remove" data-index="${index}" title="Remover">🗑️</button>
            </td>
        `;
        tbody.appendChild(row);
    });

    totalEl.textContent = formatarMoeda(total);

    document.querySelectorAll('.input-qtd').forEach(input => {
        input.addEventListener('change', (e) => {
            const idx = e.target.dataset.index;
            let val = parseInt(e.target.value);
            if (val < 1 || isNaN(val)) val = 1;
            carrinho[idx].quantidade = val;
            renderizarCarrinho();
        });
    });

    document.querySelectorAll('.btn-remove').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const idx = e.currentTarget.dataset.index;
            carrinho.splice(idx, 1);
            renderizarCarrinho();
        });
    });
}