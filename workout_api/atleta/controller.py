from uuid import uuid4
from datetime import datetime
from fastapi import APIRouter, Body, HTTPException, status, Query
from pydantic import UUID4
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from fastapi_pagination import Page, paginate

from workout_api.atleta.schemas import AtletaIn, AtletaOut, AtletaUpdate, AtletaListOut
from workout_api.atleta.models import AtletaModel
from workout_api.categorias.models import CategoriaModel
from workout_api.centro_treinamento.models import CentroTreinamentoModel
from workout_api.contrib.dependencies import DatabaseDependency

router = APIRouter()

@router.post(
    '/', 
    summary='Criar um novo Atleta',
    status_code=status.HTTP_201_CREATED,
    response_model=AtletaOut,
)
async def post(db_session: DatabaseDependency, atleta_in: AtletaIn = Body(...)) -> AtletaOut:
    categoria = (
        await db_session.execute(
            select(CategoriaModel).filter_by(nome=atleta_in.categoria.nome)
        )
    ).scalars().first()
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Categoria '{atleta_in.categoria.nome}' não encontrada."
        )

    ct = (
        await db_session.execute(
            select(CentroTreinamentoModel).filter_by(nome=atleta_in.centro_treinamento.nome)
        )
    ).scalars().first()
    if not ct:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Centro de Treinamento '{atleta_in.centro_treinamento.nome}' não encontrado."
        )

    atleta_out = AtletaOut(
        id=uuid4(),
        created_at=datetime.utcnow(),
        **atleta_in.model_dump()
    )
    atleta_model = AtletaModel(
        **atleta_out.model_dump(exclude={'categoria', 'centro_treinamento'})
    )
    atleta_model.categoria_id = categoria.pk_id
    atleta_model.centro_treinamento_id = ct.pk_id

    db_session.add(atleta_model)
    try:
        await db_session.commit()
    except IntegrityError:
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail=f"Já existe um atleta cadastrado com o cpf: {atleta_in.cpf}"
        )

    return atleta_out


@router.get(
    '/', 
    summary='Consultar todos os Atletas (com paginação)',
    status_code=status.HTTP_200_OK,
    response_model=Page[AtletaListOut],
)
async def query(
    db_session: DatabaseDependency,
    nome: str | None = Query(None, description="Filtrar por nome"),
    cpf: str | None = Query(None, description="Filtrar por CPF")
) -> Page[AtletaListOut]:
    query_stmt = select(AtletaModel)

    if nome:
        query_stmt = query_stmt.filter(AtletaModel.nome.ilike(f"%{nome}%"))
    if cpf:
        query_stmt = query_stmt.filter(AtletaModel.cpf == cpf)

    atletas = (await db_session.execute(query_stmt)).scalars().all()

    result = [
        AtletaListOut(
            nome=a.nome,
            categoria=a.categoria.nome if a.categoria else None,
            centro_treinamento=a.centro_treinamento.nome if a.centro_treinamento else None
        )
        for a in atletas
    ]

    return paginate(result)