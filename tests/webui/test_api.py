import pytest
from fastapi.testclient import TestClient
from pathlib import Path

from TARS.webui.api import app, TARSState
from TARS.config.schema import Config

# Create a mock TARSState to inject into the API
class MockTARSState:
    def __init__(self, tmp_path):
        self.workspace = tmp_path
        self.config = Config()

@pytest.fixture
def mock_tars(tmp_path):
    return MockTARSState(tmp_path)

@pytest.fixture
def client(mock_tars):
    # Override the dependency
    from TARS.webui.api import get_tars
    app.dependency_overrides[get_tars] = lambda: mock_tars
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

def test_list_workspace_in_bounds(client, mock_tars):
    # Create a dummy file
    (mock_tars.workspace / "test.txt").write_text("hello")
    response = client.get("/api/workspace?path=.")
    assert response.status_code == 200
    assert "test.txt" in response.text

def test_list_workspace_out_of_bounds(client):
    response = client.get("/api/workspace?path=../etc/passwd")
    assert response.status_code == 200
    assert "Access Denied" in response.text

def test_move_workspace_item_in_bounds(client, mock_tars):
    (mock_tars.workspace / "test.txt").write_text("hello")
    response = client.post("/api/workspace/move", data={"src": "test.txt", "dst": "test2.txt"})
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert not (mock_tars.workspace / "test.txt").exists()
    assert (mock_tars.workspace / "test2.txt").exists()

def test_move_workspace_item_out_of_bounds_src(client, mock_tars):
    response = client.post("/api/workspace/move", data={"src": "../../../etc/passwd", "dst": "test.txt"})
    assert response.status_code == 403
    assert response.json()["message"] == "Access Denied"

def test_move_workspace_item_out_of_bounds_dst(client, mock_tars):
    (mock_tars.workspace / "test.txt").write_text("hello")
    response = client.post("/api/workspace/move", data={"src": "test.txt", "dst": "../../../etc/passwd"})
    assert response.status_code == 403
    assert response.json()["message"] == "Access Denied"

def test_upload_workspace_file_in_bounds(client, mock_tars):
    response = client.post(
        "/api/workspace/upload",
        data={"path": "."},
        files={"files": ("test.txt", b"hello content")}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert (mock_tars.workspace / "test.txt").exists()
    assert (mock_tars.workspace / "test.txt").read_text() == "hello content"

def test_upload_workspace_file_out_of_bounds_dir(client, mock_tars):
    response = client.post(
        "/api/workspace/upload",
        data={"path": "../../../etc"},
        files={"files": ("test.txt", b"hello content")}
    )
    assert response.status_code == 403
    assert response.json()["message"] == "Access Denied"

def test_upload_workspace_file_out_of_bounds_filename(client, mock_tars):
    response = client.post(
        "/api/workspace/upload",
        data={"path": "."},
        files={"files": ("../../../etc/passwd", b"hello content")}
    )
    assert response.status_code == 403
    assert "Access Denied: Invalid filename" in response.json()["message"]
