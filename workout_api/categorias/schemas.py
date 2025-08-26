from pydantic import BaseModel, UUID4


class CategoriaIn(BaseModel):
    nome: str


class CategoriaOut(CategoriaIn):
    id: UUID4

    class Config:
        from_attributes = True  # <-- Isso permite conversão do SQLAlchemy -> Pydantic
