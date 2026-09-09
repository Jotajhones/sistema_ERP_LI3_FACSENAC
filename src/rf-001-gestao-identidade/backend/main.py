import sys
import os
import importlib.util
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth_router, pessoas_router

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

caminho_rf002_backend = os.path.abspath(os.path.join(BASE_DIR, '..', '..', 'rf-002-catalogo-produtos', 'backend'))

if caminho_rf002_backend not in sys.path:
    sys.path.append(caminho_rf002_backend)


caminho_arquivo = os.path.join(caminho_rf002_backend, 'routers', 'produto_router.py')
spec = importlib.util.spec_from_file_location("produto_router", caminho_arquivo)
produto_router = importlib.util.module_from_spec(spec)
sys.modules["produto_router"] = produto_router
spec.loader.exec_module(produto_router)

app = FastAPI(
    title="API - ERP Construção - RF-001",
    description="API para projeto na disciplina laboratório de inovação III - para servir aplicação web ERP.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(pessoas_router.router)

app.include_router(produto_router.router)

@app.get("/")
def health_check():
    return {"status": "online", "service": "API Para sistema ERP LAB INOVACAO III"}