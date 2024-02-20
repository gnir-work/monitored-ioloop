import asyncio
import time
import typing
from asyncio import Task
from contextvars import Context
from typing import Any, Generator, Coroutine

_T = typing.TypeVar("_T")


class MonitoredSelectorEventLoop(asyncio.SelectorEventLoop):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

    def _run_once(self, *args: Any, **kwargs: Any) -> Any:
        start = time.process_time()
        response = super()._run_once(*args, **kwargs)  # type: ignore
        print(f"Time taken: {time.process_time() - start}")
        return response

    def create_task(
        self,
        coro: Generator[Any, None, _T] | Coroutine[Any, Any, _T],
        *,
        name: object = None,
        context: Context | None = None,
    ) -> Task[Any]:
        print(f"Creating task: {coro}")
        return super().create_task(coro, name=name, context=context)


#
#
# if __name__ == '__main__':
#     # monitored_loop = MonitoredSelectorEventLoop()
#     # asyncio.set_event_loop(monitored_loop)
#     loop = asyncio.get_event_loop()
#     print(loop)
#     coru = test()
#     print("After coru creation")
#     loop.run_until_complete(coru)
#     # with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
#     #     runner.run(test())
