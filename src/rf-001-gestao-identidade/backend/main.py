import sys
import os
import importlib.util
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# MAPEAMENTO DE DIRETÓRIOS (SPRINTS)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RF002_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', '..', 'rf-002-catalogo-produtos', 'backend'))
RF004_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', '..', 'rf-004-hot-fix-orcamentos-os', 'backend'))

# CARREGADOR DINÂMICO DE ROTAS EXTERNAS
def carregar_rota_externa(nome_modulo: str, caminho_absoluto: str):
    """Carrega um router de outra pasta injetando o diretório pai no sys.path para achar os schemas/services."""
    diretorio_modulo = os.path.dirname(os.path.dirname(caminho_absoluto))
    
    # Adiciona a pasta backend do módulo no path se já não estiver
    if diretorio_modulo not in sys.path:
        sys.path.insert(0, diretorio_modulo)
        
    try:
        spec = importlib.util.spec_from_file_location(nome_modulo, caminho_absoluto)
        if spec is None:
            raise ImportError(f"Não foi possível encontrar o módulo em {caminho_absoluto}")
        modulo = importlib.util.module_from_spec(spec)
        sys.modules[nome_modulo] = modulo
        spec.loader.exec_module(modulo)
        return modulo.router
    finally:
        # Remove o diretório do path para evitar poluição global
        if diretorio_modulo in sys.path:
            sys.path.remove(diretorio_modulo)

# IMPORTAÇÃO DOS ROUTERS
# Locais (RF-001)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
from routers import auth_router, pessoas_router

# Externos (Outras Sprints)
produto_router = carregar_rota_externa(
    "produto_router", 
    os.path.join(RF002_DIR, 'routers', 'produto_router.py')
)
orcamentos_router = carregar_rota_externa(
    "orcamentos_router", 
    os.path.join(RF004_DIR, 'routers', 'orcamentos_router.py')
)
os_router = carregar_rota_externa(
    "os_router", 
    os.path.join(RF004_DIR, 'routers', 'os_router.py')
)

# CONFIGURAÇÃO DA APLICAÇÃO FASTAPI
app = FastAPI(
    title="API - ERP Construção",
    description="API para projeto na disciplina Laboratório de Inovação III - ERP Web.",
    version="1.0.0"
)

# MIDDLEWARES E CORS
origens_permitidas = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5500",
    "http://localhost:8000",
    "http://127.0.0.1:5500",
    "http://127.0.0.1:8000",
    "https://jotajhones.github.io",
    "https://sistema-erp-li3-facsenac.onrender.com",
    "https://erp-construcao.vercel.app",
    "https://sistema-erp-li-3-facsenac.vercel.app"
]

origens_extras = os.getenv("CORS_ORIGENS_EXTRAS", "")
if origens_extras:
    for origem in origens_extras.split(","):
        origem_limpa = origem.strip()
        if origem_limpa and origem_limpa not in origens_permitidas:
            origens_permitidas.append(origem_limpa)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origens_permitidas,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

@app.middleware("http")
async def aplicar_cabecalhos_seguranca(requisicao, proximo):
    resposta = await proximo(requisicao)
    resposta.headers["X-Content-Type-Options"] = "nosniff"
    resposta.headers["X-Frame-Options"] = "DENY"
    resposta.headers["X-XSS-Protection"] = "1; mode=block"
    return resposta


# REGISTRO DAS ROTAS (ENDPOINTS)
app.include_router(auth_router.router)
app.include_router(pessoas_router.router)
app.include_router(produto_router)
app.include_router(orcamentos_router)
app.include_router(os_router)


# HEALTH CHECK
@app.get("/")
def health_check():
    return {"status": "online", "service": "API Para sistema ERP LAB INOVACAO III"}