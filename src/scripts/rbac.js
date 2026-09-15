export function aplicarControleDeAcesso() {
    try {
        const userRole = localStorage.getItem('userRole');
        const roleNormalizada = userRole ? userRole.toUpperCase().trim() : '';
        const isAdministrativo = roleNormalizada === 'ADMIN' || roleNormalizada === 'GESTOR';

        const elementosRestritos = document.querySelectorAll('[data-role="admin-only"]');
        elementosRestritos.forEach(elemento => {
            if (!isAdministrativo) {
                elemento.style.display = 'none';
            } else {
                elemento.style.display = '';
            }
        });
    } catch (error) {
        console.error("Erro ao aplicar controle de acesso RBAC:", error);
    }
}

export function validarAcessibilidadeRota() {
    const userRole = localStorage.getItem('userRole');
    const roleNormalizada = userRole ? userRole.toUpperCase().trim() : '';

    if (roleNormalizada === 'CLIENTE') {
        alert("Acesso negado: você não tem permissão para acessar esta área.");
        window.location.href = '../../../rf-001-gestao-identidade/frontend/login/index.html';
        return false;
    }
    return true;
}