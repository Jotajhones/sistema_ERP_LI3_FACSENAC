
const API_URL = `${window.APP_CONFIG.API_URL}`;

export async function erpFetch(endpoint, options = {}) {
    const token = localStorage.getItem('authToken');

    if (!token) {
        window.location.href = '../../../rf-001-gestao-identidade/frontend/login/index.html';
        return;
    }

    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...options.headers
    };

    try {
        const response = await fetch(`${API_URL}${endpoint}`, {
            ...options,
            headers
        });

        if (response.status === 401) {
            localStorage.removeItem('authToken');
            localStorage.removeItem('userRole');
            alert("Sessão expirada. Por favor, faça login novamente.");
            window.location.href = '../../../rf-001-gestao-identidade/frontend/login/index.html';
            throw new Error("Não autorizado");
        }

        return response;
    } catch (error) {
        console.error("Erro de comunicação com a API:", error);
        throw error;
    }
}

