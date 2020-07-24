from fastapi import APIRouter, HTTPException, File, UploadFile, BackgroundTasks
from fastapi.responses import FileResponse
import logging, tempfile, zipfile, os, geopandas, shutil

router = APIRouter()

# could not use ArcPy (for now) due to license issues
# @router.post("/shapefile/esri", tags=["shapefile"])
# # def shapefile_esri(file: UploadFile = File(...)):
# def shapefile_esri(file: bytes = File(...)):
#
#     with tempfile.TemporaryDirectory() as temp_dir:
#         print(temp_dir)
#         os.chdir(temp_dir)
#         os.mkdir('input')
#         os.mkdir('unzipped')
#
#         print(f"working in {os.getcwd()}")
#         with open("input/zip_file.zip", 'wb') as new_file:
#             new_file.write(file)
#         print(f"output of listdir for /input {os.listdir(temp_dir + '/input')}")
#         with zipfile.ZipFile("input/zip_file.zip") as zip_file:
#             print(f"files in zip: {zip_file.namelist()}")
#             zip_file.extractall('unzipped')
#             # unzipped_files = [f for f in os.listdir('unzipped')]
#         unzipped_files = os.listdir('unzipped')
#         # print(f"output of listdir for unzipped {os.listdir('unzipped')}")
#
#     return {"did it work?": unzipped_files}

# Geopandas Simplify uses Shapely
# https://geopandas.org/reference.html#geopandas.GeoSeries.simplify
# https://shapely.readthedocs.io/en/latest/manual.html#object.simplify

# may be able to specify some params, like tolerance, with additional Form params
# https://fastapi.tiangolo.com/tutorial/request-forms-and-files/


top_level_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__))))

# background task to remove folders used to store output
def remove_output_folder(new_dir_name: str):
    print("in remove folder background task")
    # print("args", args)
    print(new_dir_name)
    # print(os.getcwd())
    # print(f"working in {os.getcwd()};; trying to remove {new_dir_name}")
    shutil.rmtree(new_dir_name)

# # https://fastapi.tiangolo.com/advanced/custom-response/
# using File response which requires async
@router.post("/shapefile/geopandas", tags=["shapefile"])
async def shapefile_geopandas(background_tasks: BackgroundTasks, file: bytes = File (...)):
    # for some reason the FastAPI/Starlette FileResponse cannot find the file
    # in the TemporaryDirectory, so we need to create a path it can find
    # and remove it after
    output_dir_name = 'output'
    os.makedirs(os.path.join(top_level_path, output_dir_name), exist_ok=True)
    print("new folder exists? ", os.listdir(top_level_path))
    output_path = os.path.join(top_level_path, output_dir_name)
    print("new up top - ", output_path)

    background_tasks.add_task(remove_output_folder, output_path)

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        os.mkdir('input')
        os.mkdir('unzipped')
        os.mkdir('processed')
        os.mkdir('output')

        with open("input/zip_file.zip", 'wb') as new_file:
            new_file.write(file)
        # because the zipfile is binary zipped shapefile, Fiona would require us
        # to use ZipMemoryFile (https://fiona.readthedocs.io/en/latest/manual.html#memoryfile-and-zipmemoryfile), which requires knowing the name of the shapefile
        # with ZipMemoryFile(data) as zip:
        with zipfile.ZipFile("input/zip_file.zip") as zip_file:
            zip_file.extractall('unzipped')
        shp_file = [f for f in os.listdir('unzipped') if '.shp' in f][0]
        df = geopandas.read_file("unzipped/" + shp_file)
        print(f"input projection = {df.crs}")

        simplified_gs = df.simplify(0.2) # preserve_topology = True by default
        simplified_gs.to_file("processed/simplified.shp")
        # print(f"listing contents of temp_dir {os.listdir(temp_dir)}")
        listing = os.listdir("processed")

        # make zip file
        archive_name = "output/simplified_polygon"
        shutil.make_archive(archive_name, "zip", "processed")
        print(f"file there? {os.listdir('output')}")

        full_path = os.path.abspath("output/simplified_polygon.zip")
        print("path is", full_path)
        print("is zip file?", zipfile.is_zipfile(full_path))

        shutil.move(full_path, output_path)
        full_output_path = os.path.join(output_path, "simplified_polygon.zip")
        with zipfile.ZipFile(full_output_path) as zipped:
            print("in zipped: ", zipped.namelist())

        # open(os.path.join(tmp_dir,'file.txt'), 'w')
        # output_file_path = os.path.join(temp_dir, "/output/simplified_polygon.zip")

    return FileResponse(full_output_path)
        # https://stackoverflow.com/questions/6977544/rar-zip-files-mime-type

        # not sure if we should be using StreamingResponse or FileResponse

    # return {"what do we have?": listing}


@router.post("/geojson/", tags=["shapefile"])
def accept_geojson(file: UploadFile = File(...)):
    print(f"file: {file}")
    root.info("file: {file}")
    return {"did it work?": root.info("file: {file}")}
