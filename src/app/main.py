from fastapi import FastAPI, File, UploadFile

from app.api import uploads, simplify_polygon

app = FastAPI()


app.include_router(
    uploads.router,
    prefix="/uploads"
)
app.include_router(
    simplify_polygon.router,
    prefix="/simplify_polygon"
)
