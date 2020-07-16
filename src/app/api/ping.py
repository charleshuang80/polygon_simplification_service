from fastapi import APIRouter

router = APIRouter()

@router.get("/ping")
async def pong():
    # https://fastapi.tiangolo.com/async/
    # some async operation
    # results = await some_library()
    return {"ping": "pong!"}
