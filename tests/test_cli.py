from intern_app.cli import main


def test_config_command_runs_and_hides_values(capsys, monkeypatch):
    monkeypatch.setenv("MUSE_API_KEY", "sk-not-a-real-key")
    from intern_app import config

    config.settings.cache_clear()

    assert main(["config"]) == 0
    out = capsys.readouterr().out
    assert "sk-not-a-real-key" not in out
    assert "set      MUSE_API_KEY" in out
    config.settings.cache_clear()


def test_status_command_runs_against_a_temp_database(capsys, monkeypatch, tmp_path):
    monkeypatch.setenv("INTERN_APP_DB", str(tmp_path / "t.db"))
    from intern_app import config

    config.settings.cache_clear()

    assert main(["status"]) == 0
    out = capsys.readouterr().out
    assert "No listings stored yet." in out
    assert "quota left" in out
    assert "LLM calls 0 total" in out
    config.settings.cache_clear()
