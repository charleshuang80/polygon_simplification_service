from fastapi import FastAPI, File, UploadFile

from app.api import ping, simplify_polygon

app = FastAPI()


app.include_router(ping.router)
# being complained about
app.include_router(
    simplify_polygon.router,
    prefix="/simplify_polygon"
)
