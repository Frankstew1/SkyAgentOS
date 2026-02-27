from evals.browser.login_flow_eval import run_eval as browser_eval
from evals.desktop.file_ops_eval import run_eval as desktop_eval


def run_eval() -> dict:
    b = browser_eval()
    d = desktop_eval()
    return {"passed": b["passed"] and d["passed"], "browser": b, "desktop": d}


if __name__ == "__main__":
    print(run_eval())
