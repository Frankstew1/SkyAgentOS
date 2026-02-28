import os
from pathlib import Path

from skyagentos.tools.desktop_tool import DesktopTool


def test_desktop_tool_dry_run(tmp_path: Path):
    os.environ["SKYAGENT_DRY_RUN"] = "true"
    tool = DesktopTool("http://desktop-daemon:8890", artifact_dir=tmp_path)
    result, artifact = tool.execute("run-1", "step-1", "operate", {"prompt": "open file"})
    assert result["runtime"] == "desktop"
    assert artifact.kind == "desktop_trace"
