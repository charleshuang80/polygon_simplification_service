from fastapi import APIRouter, HTTPException, File, UploadFile

router = APIRouter()

@router.get("/test")
def test():
    # https://fastapi.tiangolo.com/async/
    # some async operation
    # results = await some_library()
    return {"test": "passed!"}

@router.post("/test_file")
# example uses async https://fastapi.tiangolo.com/tutorial/request-files/
def create_file(file: bytes = File(...)):
    return {"file_size": len(file)}
    # return {"something": 5}

@router.post("/test_uploadfile")
# example uses async https://fastapi.tiangolo.com/tutorial/request-files/
def create_upload_file(file: UploadFile = File(...)):
    return {"filename": file.filename}
