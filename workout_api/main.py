from fastapi import FastAPI
from workout_api.atleta.controller import router as atleta_router
from workout_api.categorias.controller import router as categoria_router
from workout_api.centro_treinamento.controller import router as ct_router

from fastapi_pagination import add_pagination

app = FastAPI(title="Workout API")

# Rotas
app.include_router(atleta_router, prefix="/atletas", tags=["Atletas"])
app.include_router(categoria_router, prefix="/categorias", tags=["Categorias"])
app.include_router(ct_router, prefix="/centros-treinamento", tags=["Centros de Treinamento"])

# Habilitar paginação
add_pagination(app)