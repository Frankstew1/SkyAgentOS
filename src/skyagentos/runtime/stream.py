from __future__ import annotations

import json
from typing import Callable


def default_stream(channel: str, payload: dict) -> None:
    print(json.dumps({"channel": channel, **payload}))


StreamFn = Callable[[str, dict], None]
