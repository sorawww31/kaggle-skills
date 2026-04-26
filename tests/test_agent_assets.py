# tests/test_agent_assets.py
# Where: repository tests for AI-agent configuration.
# What: Validates generated adapters and MCP config syntax.
# Why: Catch stale or malformed cross-agent setup before it reaches users.

from __future__ import annotations

import importlib.util
import json
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KAGGLE_MCP_URL = "https://www.kaggle.com/mcp"


def _load_sync_module():
    module_path = ROOT/ "sync_agent_assets.py"
    spec = importlib.util.spec_from_file_location("sync_agent_assets", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sync_agent_assets = _load_sync_module()
render_files = sync_agent_assets.render_files


def _write_minimal_agent_sources(root: Path) -> None:
    (root / "AGENTS.md").write_text("# Shared instructions\n", encoding="utf-8")

    command_dir = root / ".agents" / "commands"
    command_dir.mkdir(parents=True)
    (command_dir / "sample.md").write_text("# Sample command\n", encoding="utf-8")

    skill_dir = root / ".agents" / "skills" / "sample"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("# Sample skill\n", encoding="utf-8")


def _delete_sample_shared_sources(root: Path) -> None:
    (root / ".agents" / "commands" / "sample.md").unlink()
    (root / ".agents" / "skills" / "sample" / "SKILL.md").unlink()


def _sample_generated_paths() -> set[str]:
    return {
        ".claude/commands/sample.md",
        ".cursor/commands/sample.md",
        ".github/prompts/sample.prompt.md",
        ".gemini/commands/sample.toml",
        ".claude/skills/sample/SKILL.md",
    }


def test_generated_agent_assets_are_current() -> None:
    for path, expected in render_files(ROOT).items():
        assert path.exists(), f"{path.relative_to(ROOT)} is missing"
        assert path.read_bytes() == expected, f"{path.relative_to(ROOT)} is stale"


def test_sync_keeps_generated_assets_without_prune(tmp_path: Path) -> None:
    _write_minimal_agent_sources(tmp_path)
    written, removed = sync_agent_assets.write_files(tmp_path)
    assert written
    assert not removed

    _delete_sample_shared_sources(tmp_path)
    expected_removed = _sample_generated_paths()
    stale = {
        path.relative_to(tmp_path).as_posix()
        for path in sync_agent_assets.check_files(tmp_path)
    }
    assert expected_removed.isdisjoint(stale)

    written, removed = sync_agent_assets.write_files(tmp_path)
    assert not written
    assert not removed
    for relative_path in expected_removed:
        assert (tmp_path / relative_path).exists()


def test_sync_removes_generated_assets_with_prune(tmp_path: Path) -> None:
    _write_minimal_agent_sources(tmp_path)
    written, removed = sync_agent_assets.write_files(tmp_path)
    assert written
    assert not removed

    _delete_sample_shared_sources(tmp_path)
    expected_removed = _sample_generated_paths()
    stale = {
        path.relative_to(tmp_path).as_posix()
        for path in sync_agent_assets.check_files(tmp_path, prune=True)
    }
    assert expected_removed <= stale

    written, removed = sync_agent_assets.write_files(tmp_path, prune=True)
    assert not written
    assert {
        path.relative_to(tmp_path).as_posix() for path in removed
    } == expected_removed
    for relative_path in expected_removed:
        assert not (tmp_path / relative_path).exists()
    assert not (tmp_path / ".claude" / "skills" / "sample").exists()


def test_mcp_configs_parse_and_point_to_kaggle() -> None:
    claude = json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8"))
    cursor = json.loads((ROOT / ".cursor" / "mcp.json").read_text(encoding="utf-8"))
    gemini = json.loads(
        (ROOT / ".gemini" / "settings.json").read_text(encoding="utf-8")
    )
    vscode = json.loads((ROOT / ".vscode" / "mcp.json").read_text(encoding="utf-8"))
    codex = tomllib.loads((ROOT / ".codex" / "config.toml").read_text(encoding="utf-8"))

    assert claude["mcpServers"]["kaggle"]["url"] == KAGGLE_MCP_URL
    assert cursor["mcpServers"]["kaggle"]["url"] == KAGGLE_MCP_URL
    assert gemini["mcpServers"]["kaggle"]["httpUrl"] == KAGGLE_MCP_URL
    assert vscode["servers"]["kaggle"]["url"] == KAGGLE_MCP_URL
    assert codex["mcp_servers"]["kaggle"]["url"] == KAGGLE_MCP_URL
    assert codex["mcp_servers"]["kaggle"]["bearer_token_env_var"] == "KAGGLE_API_TOKEN"


def test_generated_gemini_commands_parse() -> None:
    command_dir = ROOT / ".gemini" / "commands"
    for command_file in command_dir.glob("*.toml"):
        parsed = tomllib.loads(command_file.read_text(encoding="utf-8"))
        assert parsed["description"]
        assert parsed["prompt"]
