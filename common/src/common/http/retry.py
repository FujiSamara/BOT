from typing import Callable


def retry(times: int = 5, ignored: list[Exception] | None = None):
    """Decorates callable with retrying it `times` times.

    - Note Retries work only for python `Exception`.
    Args:
        ignored: list of exception which throw without retrying.
    """
    if ignored is None:
        ignored = []

    def wrap(func: Callable):
        async def repeat_request(*args, **kwargs):
            times_left = times
            while True:
                try:
                    times_left -= 1
                    return await func(*args, **kwargs)
                except ignored:
                    raise
                except Exception:
                    if not times_left:
                        raise

        return repeat_request

    return wrap
