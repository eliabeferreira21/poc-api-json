from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_upload_file():
    response = client.post("/upload/", files={"file": ("test.json", b'[{"name": "Test", "email": "test@test.com", "age": 30}]')})
    assert response.status_code == 200
    assert "id" in response.json()