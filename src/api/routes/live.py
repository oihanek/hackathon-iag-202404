from fastapi import APIRouter

router = APIRouter()


@router.get("/live")
def hello() -> str:
    """ Alive check point"""
    return "alive"

