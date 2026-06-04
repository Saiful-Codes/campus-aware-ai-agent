import importlib
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))


def test_influxdb_url_default_uses_port_18086(monkeypatch):
    # Suppress backend/.env so we actually exercise the in-code default
    # rather than the value developers happen to have set locally.
    import dotenv

    monkeypatch.setattr(dotenv, "load_dotenv", lambda *args, **kwargs: False)
    monkeypatch.delenv("INFLUXDB_URL", raising=False)

    import app.core.config as config_module
    importlib.reload(config_module)

    assert config_module.settings.INFLUXDB_URL.endswith(":18086")
