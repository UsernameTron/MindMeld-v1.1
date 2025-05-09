from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()
data_router = APIRouter()

@router.get("/")
@data_router.get("/")
def get_data():
    return JSONResponse(content={"value": "This is your dashboard data!"})
