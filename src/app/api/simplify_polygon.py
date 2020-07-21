from fastapi import APIRouter, HTTPException, File, UploadFile
import logging, tempfile, zipfile, os
# import arcpy

router = APIRouter()


root = logging.getLogger()
root.setLevel(logging.INFO)

log_format = '%(asctime)s %(filename)s: %(message)s'
logging.basicConfig(filename="test.log", format=log_format)

@router.post("/shapefile/")
def shapefile(file: UploadFile = File(...)):
    answer = False
    print(f"file: {file}")
    # root.info("file: {file}")
    return {"did it work?": root.info("file: {file}")}

@router.post("/shapefile/esri")
# def shapefile_esri(file: UploadFile = File(...)):
def shapefile_esri(file: bytes = File(...)):

    with tempfile.TemporaryDirectory() as temp_dir:
        print(temp_dir)
        os.chdir(temp_dir)
        os.mkdir('input')
        os.mkdir('unzipped')

        print(f"working in {os.getcwd()}")
        with open("input/zip_file.zip", 'wb') as new_file:
            new_file.write(file)
        print(f"output of listdir for /input {os.listdir(temp_dir + '/input')}")
        with zipfile.ZipFile("input/zip_file.zip") as zip_file:
            print(f"files in zip: {zip_file.namelist()}")
            zip_file.extractall('unzipped')
            # unzipped_files = [f for f in os.listdir('unzipped')]
        unzipped_files = os.listdir('unzipped')
        # print(f"output of listdir for unzipped {os.listdir('unzipped')}")

    return {"did it work?": unzipped_files}


@router.post("/geojson/")
def accept_geojson(file: UploadFile = File(...)):
    print(f"file: {file}")
    root.info("file: {file}")
    return {"did it work?": root.info("file: {file}")}
