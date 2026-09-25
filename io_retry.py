"""Retry transient Windows write-open failures during large local builds."""

import time


def write_text(path, value, *, encoding="utf-8"):
    for attempt in range(4):
        try:
            return path.write_text(value, encoding=encoding)
        except OSError as error:
            if error.errno != 22 or attempt == 3:
                raise
            time.sleep(0.1 * (attempt + 1))
