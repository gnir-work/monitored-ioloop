import time

BLOCK_THRESHOLD = 0.075


def busy_wait(seconds_to_wait: float = 1) -> None:
    now = time.perf_counter()
    while time.perf_counter() - now < seconds_to_wait:
        pass


def _check_monitor_result(
    expected_block: float, monitored_block: float, threshold: float = BLOCK_THRESHOLD
) -> None:
    assert (
        expected_block * (1 - threshold)
        < monitored_block
        < expected_block * (1 + threshold)
    ), f"Expected: {expected_block}, Monitored: {monitored_block}, Threshold: {threshold}"
