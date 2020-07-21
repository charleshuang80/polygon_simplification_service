from starlette.testclient import TestClient
import zipfile, os


# test for methods to get things working, accepting files, and unzipping received files
def test_test(test_app):
    response = test_app.get("/uploads/test")
    assert response.status_code == 200
    assert response.json() == {"test": "passed!"}

def test_create_file(test_app):
    files = {"file": open("tests/test_files/fake_text_file.txt", "rb")}
    response = test_app.post("/uploads/test_file", files=files)
    assert response.status_code == 200
    assert response.json() == {"file_size": 3771}

def test_create_upload_file(test_app):
    files = {"file": open("tests/test_files/fake_text_file.txt", "rb")}
    response = test_app.post("/uploads/test_uploadfile", files=files)
    assert response.status_code == 200
    assert response.json() == {"filename": "fake_text_file.txt"}

# these tests are not currently working because reading or properly sending
# the zip file needs some work.
# def test_unzip_file(test_app):
#     files = {"file": open("tests/test_files/africa.zip", "r")}
#     response = test_app.post("/uploads/test_file/unzip", files=files)
#     assert response.status_code == 200
#     assert response.json() == {"unzipped files":["africa.prj","africa.shx","africa.cpg","africa.shp","africa.qpj"]}

# def test_unzip_upload_file(test_app):
#     print(f"working in {os.getcwd()}")
#     print(f"things in tests/test_files {os.listdir('/tests/test_files')}")
#     files = {"file": open("tests/test_files/africa.zip", "rb")}
#     files = {"file": zipfile.ZipFile("tests/test_files/africa.zip", "r")}
#     response = test_app.post("/uploads/test_uploadfile/unzip", files=files)
#     assert response.status_code == 200
#     assert response.json() == {"unzipped files":["africa.prj","africa.shx","africa.cpg","africa.shp","africa.qpj"]}
