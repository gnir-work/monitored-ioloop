import time


def busy_wait(seconds_to_wait: float = 1) -> None:
    now = time.perf_counter()
    while time.perf_counter() - now < seconds_to_wait:
        pass
