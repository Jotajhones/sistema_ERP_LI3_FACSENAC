import sys
import os
import importlib.util


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import auth_router, pessoas_router

caminho_rf002_backend = os.path.abspath(
    os.path.join
        (BASE_DIR,
         '..',
         '..',
         'rf-002-catalogo-produtos',
         'backend'
     )
)

if caminho_rf002_backend not in sys.path:
    sys.path.append(caminho_rf002_backend)

caminho_arquivo = os.path.join(
    caminho_rf002_backend,
    'routers', 
    'produto_router.py'
)

spec = importlib.util.spec_from_file_location("produto_router", caminho_arquivo)

produto_router = importlib.util.module_from_spec(spec)

sys.modules["produto_router"] = produto_router

try:
    spec.loader.exec_module(produto_router)

finally:
    if sys.path[0] == caminho_rf002_backend:
        sys.path.pop(0)

spec.loader.exec_module(produto_router)

app = FastAPI(
    title="API - ERP Construção - RF-001",
    description="API para projeto na disciplina laboratório de inovação III - para servir aplicação web ERP.",
    version="1.0.0"
)

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


app.include_router(auth_router.router)
app.include_router(pessoas_router.router)

app.include_router(produto_router.router)

@app.get("/")
def health_check():
    return {"status": "online", "service": "API Para sistema ERP LAB INOVACAO III"}