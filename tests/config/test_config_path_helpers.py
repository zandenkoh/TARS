from pathlib import Path
from TARS.config.paths import get_cli_history_path, get_bridge_install_dir

def test_cli_history_path_uses_config_path(monkeypatch, tmp_path: Path):
    mock_config_path = tmp_path / "config.json"
    monkeypatch.setattr("TARS.config.paths.get_config_path", lambda: mock_config_path)

    assert get_cli_history_path() == mock_config_path / ".history"

def test_bridge_install_dir_uses_config_path(monkeypatch, tmp_path: Path):
    mock_config_path = tmp_path / "config.json"
    monkeypatch.setattr("TARS.config.paths.get_config_path", lambda: mock_config_path)

    assert get_bridge_install_dir() == mock_config_path / ".bridge"
