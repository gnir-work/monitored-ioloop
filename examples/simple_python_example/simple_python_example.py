from monitored_ioloop.monitored_asyncio import monitored_asyncio_loop_factory
from monitored_ioloop.monitoring import IoLoopMonitorState
import asyncio
import logging
import time

logger = logging.getLogger("simple_python_example")


async def main() -> None:
    async def non_blocking_sleep(coroutine_id: int) -> None:
        logger.info(f"[id: {coroutine_id}] Before non-blocking sleep")
        await asyncio.sleep(1)
        logger.info(f"[id: {coroutine_id}] After non-blocking sleep")

    async def blocking_sleep(coroutine_id: int) -> None:
        logger.info(f"[id: {coroutine_id}] Before blocking sleep")
        time.sleep(1)
        logger.info(f"[id: {coroutine_id}] After blocking sleep")

    await asyncio.gather(
        non_blocking_sleep(coroutine_id=0),
        blocking_sleep(coroutine_id=1),
        non_blocking_sleep(coroutine_id=2),
        non_blocking_sleep(coroutine_id=3),
        blocking_sleep(coroutine_id=4),
        non_blocking_sleep(coroutine_id=5),
    )


def monitor(ioloop_monitor_state: IoLoopMonitorState) -> None:
    if ioloop_monitor_state.callback_wall_time > 0.1:
        logger.warning(
            f"Blocking operation detected, executing of {ioloop_monitor_state.callback_pretty_name} "
            f"took: {ioloop_monitor_state.callback_wall_time}"
        )
    if ioloop_monitor_state.loop_lag > 0.1:
        logger.warning(
            f"Task {ioloop_monitor_state.callback_pretty_name} was executed after "
            f"a significant delay: {ioloop_monitor_state.loop_lag}"
        )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        datefmt="[%d-%b-%y %H:%M:%S]",
        format="%(asctime)s %(message)s",
    )
    logger.info("starting")
    loop_factory = monitored_asyncio_loop_factory(monitor_callback=monitor)
    logger.info("Created loop factory")
    asyncio.run(main(), loop_factory=loop_factory)
