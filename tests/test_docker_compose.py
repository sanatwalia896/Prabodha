from pathlib import Path


def test_compose_manifest_contains_core_services() -> None:
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")

    assert "focus-db" in compose
    assert "focus-media" in compose
    assert "focus-network" in compose
