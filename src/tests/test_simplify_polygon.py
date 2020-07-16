from starlette.testclient import TestClient
# import os

# from app.main import app
def test_test(test_app):
    response = test_app.get("/simplify_polygon/test")
    assert response.status_code == 200
    assert response.json() == {"test": "passed!"}

def test_create_file(test_app):
    files = {"file": open("tests/fake_text_file.txt", "rb")}
    response = test_app.post("/simplify_polygon/test_file", files=files)
    assert response.status_code == 200
    assert response.json() == {"file_size": 3771}

def test_create_upload_file(test_app):
    files = {"file": open("tests/fake_text_file.txt", "rb")}
    response = test_app.post("/simplify_polygon/test_uploadfile", files=files)
    assert response.status_code == 200
    assert response.json() == {"filename": "fake_text_file.txt"}
