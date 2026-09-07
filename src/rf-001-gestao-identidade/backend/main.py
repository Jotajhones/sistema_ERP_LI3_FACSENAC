from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth_router, pessoas_router, produtos_router

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
app.include_router(produtos_router.router)

@app.get("/")
def health_check():
    return {"status": "online", "service": "API MVC+S Estruturada"}