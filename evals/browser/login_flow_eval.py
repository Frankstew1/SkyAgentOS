from workers.browser_worker.src.session_manager import BrowserSessionManager


def run_eval() -> dict:
    out = BrowserSessionManager().execute("login_flow", {"objective": "Login and capture dashboard"})
    return {"passed": out.get("status") == "ok", "details": out}


if __name__ == "__main__":
    print(run_eval())
