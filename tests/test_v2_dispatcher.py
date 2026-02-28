from services.orchestrator.src.mission.models import StepV2
from services.orchestrator.src.runtime.dispatcher import Dispatcher
from workers.browser_worker.src.session_manager import BrowserSessionManager
from workers.desktop_worker.src.controller import DesktopController


class DummyWorkspace:
    def execute(self, action: str, payload: dict) -> dict:
        return {"status": "ok", "runtime": "workspace", "action": action}


class DummyTool:
    def execute(self, action: str, payload: dict) -> dict:
        return {"status": "ok", "runtime": "tools", "action": action}


def test_dispatcher_routes_runtime():
    d = Dispatcher(BrowserSessionManager(), DesktopController(), DummyWorkspace(), DummyTool())
    out = d.dispatch(StepV2(step_id="s1", mission_id="m1", runtime="desktop", action="operate"))
    assert out["runtime"] == "desktop"
