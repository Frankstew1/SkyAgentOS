from workers.desktop_worker.src.controller import DesktopController


def run_eval() -> dict:
    out = DesktopController().execute("file_ops", {"objective": "Organize files"})
    return {"passed": out.get("status") == "ok", "details": out}


if __name__ == "__main__":
    print(run_eval())
