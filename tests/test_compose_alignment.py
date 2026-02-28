from pathlib import Path


def test_main_compose_has_ollama_pull_and_desktop_daemon():
    text = Path("docker-compose.yml").read_text(encoding="utf-8")
    assert "ollama-pull:" in text
    assert "desktop-daemon:" in text
    assert "skyagentos.api.main" in text


def test_dev_compose_uses_module_entrypoints():
    text = Path("infra/docker/docker-compose.dev.yml").read_text(encoding="utf-8")
    assert 'python", "-m", "skyagentos.api.main", "serve"' in text
    assert 'python", "-m", "skyagentos.api.main", "benchmark"' in text
