from fastapi import APIRouter


router = APIRouter(prefix='/product')


@router.get('/')
async def get_all_products():
    ...


@router.get('/{id}/')
async def get_product(id: int):
    ...
