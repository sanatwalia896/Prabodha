from pathlib import Path


def test_compose_manifest_contains_core_services() -> None:
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")

    assert "focus-backend" in compose
    assert "focus-ui" in compose
    assert "focus-db" in compose
    assert "focus-cache" in compose
    assert "focus-ai" in compose
    assert "focus-cv" in compose
    assert "focus-network" in compose
