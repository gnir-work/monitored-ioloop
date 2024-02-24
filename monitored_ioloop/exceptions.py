class NoUvLoopInstalled(ImportError):
    def __init__(self) -> None:
        super().__init__(
            "Please install uvloop compatible version via `pip install monitored_ioloop[uvloop]`"
        )
