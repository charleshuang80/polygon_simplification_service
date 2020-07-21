from fastapi import APIRouter, HTTPException, File, UploadFile
import logging, tempfile, zipfile, os

router = APIRouter()

# initial methods used to get things up and running
@router.get("/test")
def test():
    # https://fastapi.tiangolo.com/async/
    # some async operation
    # results = await some_library()
    return {"test": "passed!"}

# testing a file upload with File
@router.post("/test_file")
# example uses async https://fastapi.tiangolo.com/tutorial/request-files/
def create_file(file: bytes = File(...)):
    return {"file_size": len(file)}
    # return {"something": 5}

# testing a file upload with UploadFile
@router.post("/test_uploadfile")
# example uses async https://fastapi.tiangolo.com/tutorial/request-files/
def create_upload_file(file: UploadFile = File(...)):
    return {"filename": file.filename}

# ability to accept a zip file and unzip it with File
@router.post("/test_file/unzip")
def unzip_file(file: bytes = File(...)):

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        os.mkdir('input')
        os.mkdir('unzipped')

        with open("input/zip_file.zip", 'wb') as new_file:
            new_file.write(file)
            # print(f"output of listdir for /input {os.listdir(temp_dir + '/input')}")

            with zipfile.ZipFile("input/zip_file.zip") as zip_file:
                print(f"files in zip: {zip_file.namelist()}")
                zip_file.extractall('unzipped')

        unzipped_files = os.listdir('unzipped')

    return {"unzipped files": unzipped_files}

# ability to accept a zip file and unzip it with UploadFile
@router.post("/test_uploadfile/unzip")
def unzip_upload_file(file: UploadFile = File(...)):

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        os.mkdir('input')
        os.mkdir('unzipped')

        with open("input/zip_file.zip", 'wb') as new_file:
            new_file.write(file.file._file.getvalue())
            # print(f"output of listdir for /input {os.listdir(temp_dir + '/input')}")

            with zipfile.ZipFile("input/zip_file.zip") as zip_file:
                print(f"files in zip: {zip_file.namelist()}")
                zip_file.extractall('unzipped')

        unzipped_files = os.listdir('unzipped')

    return {"unzipped files": unzipped_files}
