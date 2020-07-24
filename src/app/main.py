from fastapi import FastAPI, File, UploadFile

from app.api import uploads, simplify_polygon

tags_metadata = [
    {
        "name": "shapefile",
        "description": "service to accept a polygon via zipped shapefile, and return a simplified polygon"
    },
    {
        "name": "test",
        "description": "endpoints set up to get things working, and test accepting files and unzipping files"
    }
]

app = FastAPI(
    title="Polygon Simplification Service",
    description="A service to simplify polygons, ICP-6 from the EED PI 20.2 Innovation Challenge",
    version="0.0.1",
    openapi_tags=tags_metadata
)


app.include_router(
    uploads.router,
    prefix="/uploads"
)
app.include_router(
    simplify_polygon.router,
    prefix="/simplify_polygon"
)
