import typing
from asyncio import tasks
from asyncio.events import Handle


def pretty_format_handle(handle: Handle) -> str:
    callback = handle._callback  # type: ignore
    if isinstance(getattr(callback, "__self__", None), tasks.Task):
        # format the task
        return repr(callback.__self__)
    else:
        return repr(handle)


def pretty_callback_name(callback: typing.Callable[..., typing.Any]) -> str:
    if isinstance(getattr(callback, "__self__", None), tasks.Task):
        # format the task
        return repr(callback.__self__)  # type: ignore
    else:
        return repr(callback)
