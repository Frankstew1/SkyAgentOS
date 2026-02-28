import os
from pathlib import Path

from skyagentos.tools.skyvern_tool import SkyvernTool


def test_skyvern_tool_uses_prompt_field_in_dry_run(tmp_path: Path):
    os.environ["SKYAGENT_DRY_RUN"] = "true"
    tool = SkyvernTool("http://skyvern:8000", artifact_dir=tmp_path)
    result, _ = tool.execute(
        "run-1", "step-1", {"prompt": "Do a task", "url": "https://example.com"}
    )
    assert result["request"]["prompt"] == "Do a task"
    assert result["request"]["url"] == "https://example.com"
