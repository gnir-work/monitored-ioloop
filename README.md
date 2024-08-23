# Monitored IO Loop
A production ready monitored IO loop for Python.  
No more wondering why your event loop (or random pieces of your code) are suddenly popping up as slow in your monitoring.

![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/gnir-work/monitored-ioloop/test_and_lint_package.yaml)
![PyPI - Version](https://img.shields.io/pypi/v/monitored_ioloop)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/monitored_ioloop)


## Getting started
### Installation
```bash
pip install monitored_ioloop  # For the default event loop
pip install monitored_ioloop[uvloop]  # For the the additional support of the uvloop event loop
```

### Demo
:pencil2: [Play with the demo in sandbox](https://codesandbox.io/p/devbox/monitored-ioloop-example-d924q4?layout=%257B%2522sidebarPanel%2522%253A%2522EXPLORER%2522%252C%2522rootPanelGroup%2522%253A%257B%2522direction%2522%253A%2522horizontal%2522%252C%2522contentType%2522%253A%2522UNKNOWN%2522%252C%2522type%2522%253A%2522PANEL_GROUP%2522%252C%2522id%2522%253A%2522ROOT_LAYOUT%2522%252C%2522panels%2522%253A%255B%257B%2522type%2522%253A%2522PANEL_GROUP%2522%252C%2522contentType%2522%253A%2522UNKNOWN%2522%252C%2522direction%2522%253A%2522vertical%2522%252C%2522id%2522%253A%2522clt4i5fqk00063b6ii5cdc95p%2522%252C%2522sizes%2522%253A%255B70%252C30%255D%252C%2522panels%2522%253A%255B%257B%2522type%2522%253A%2522PANEL_GROUP%2522%252C%2522contentType%2522%253A%2522EDITOR%2522%252C%2522direction%2522%253A%2522horizontal%2522%252C%2522id%2522%253A%2522EDITOR%2522%252C%2522panels%2522%253A%255B%257B%2522type%2522%253A%2522PANEL%2522%252C%2522contentType%2522%253A%2522EDITOR%2522%252C%2522id%2522%253A%2522clt4i5fqk00023b6i5fk9mavr%2522%257D%255D%257D%252C%257B%2522type%2522%253A%2522PANEL_GROUP%2522%252C%2522contentType%2522%253A%2522SHELLS%2522%252C%2522direction%2522%253A%2522horizontal%2522%252C%2522id%2522%253A%2522SHELLS%2522%252C%2522panels%2522%253A%255B%257B%2522type%2522%253A%2522PANEL%2522%252C%2522contentType%2522%253A%2522SHELLS%2522%252C%2522id%2522%253A%2522clt4i5fqk00043b6i2xok8884%2522%257D%255D%252C%2522sizes%2522%253A%255B100%255D%257D%255D%257D%252C%257B%2522type%2522%253A%2522PANEL_GROUP%2522%252C%2522contentType%2522%253A%2522DEVTOOLS%2522%252C%2522direction%2522%253A%2522vertical%2522%252C%2522id%2522%253A%2522DEVTOOLS%2522%252C%2522panels%2522%253A%255B%257B%2522type%2522%253A%2522PANEL%2522%252C%2522contentType%2522%253A%2522DEVTOOLS%2522%252C%2522id%2522%253A%2522clt4i5fqk00053b6ijbk7icqr%2522%257D%255D%252C%2522sizes%2522%253A%255B100%255D%257D%255D%252C%2522sizes%2522%253A%255B100%252C0%255D%257D%252C%2522tabbedPanels%2522%253A%257B%2522clt4i5fqk00023b6i5fk9mavr%2522%253A%257B%2522id%2522%253A%2522clt4i5fqk00023b6i5fk9mavr%2522%252C%2522tabs%2522%253A%255B%255D%257D%252C%2522clt4i5fqk00053b6ijbk7icqr%2522%253A%257B%2522id%2522%253A%2522clt4i5fqk00053b6ijbk7icqr%2522%252C%2522tabs%2522%253A%255B%255D%257D%252C%2522clt4i5fqk00043b6i2xok8884%2522%253A%257B%2522id%2522%253A%2522clt4i5fqk00043b6i2xok8884%2522%252C%2522activeTabId%2522%253A%2522clt4i5fqk00033b6i0vl1qm5r%2522%252C%2522tabs%2522%253A%255B%257B%2522id%2522%253A%2522clt4i5fqk00033b6i0vl1qm5r%2522%252C%2522mode%2522%253A%2522permanent%2522%252C%2522type%2522%253A%2522TASK_LOG%2522%252C%2522taskId%2522%253A%2522start%2522%257D%252C%257B%2522id%2522%253A%2522clt4i7i7h00d03b6incbja8w8%2522%252C%2522mode%2522%253A%2522permanent%2522%252C%2522type%2522%253A%2522TERMINAL%2522%252C%2522shellId%2522%253A%2522clt4i9ozn01d0d9hv8ftm7tt1%2522%257D%255D%257D%257D%252C%2522showDevtools%2522%253Afalse%252C%2522showShells%2522%253Atrue%252C%2522showSidebar%2522%253Atrue%252C%2522sidebarPanelSize%2522%253A15%257D)


### Usage
#### Asyncio event loop

```python
from monitored_ioloop.monitored_asyncio import MonitoredAsyncIOEventLoopPolicy
from monitored_ioloop.monitoring import IoLoopMonitorState
import asyncio
import time


def monitor_callback(ioloop_state: IoLoopMonitorState) -> None:
    print(ioloop_state)


async def test_coroutine() -> None:
    time.sleep(2)


def main():
    asyncio.set_event_loop_policy(MonitoredAsyncIOEventLoopPolicy(monitor_callback))
    asyncio.run(test_coroutine())
```

#### Uvloop event loop
In order to use the uvloop event loop, please make sure to install `monitored_ioloop[uvloop]`.  
The usage is the same as the asyncio event loop, but with `monitored_ioloop.monitored_uvloop.MonitoredUvloopEventLoopPolicy` instead of the `monitored_ioloop.monitored_asyncio.MonitoredAsyncIOEventLoopPolicy`.

## The monitor callback
The monitor callback will be called for every execution that the event loop initiates.  
With every call you will receive an [IoLoopMonitorState](monitored_ioloop/monitoring.py) object that contains the following information:
- `callback_wall_time`: Wall executing time of the callback.
- `loop_handles_count`: The amount of handles (think about them as tasks) that the IO loop is currently handling.
- `loop_lag`: The amount of time it took from the moment the task was added to the loop until it was executed.
- `callback_pretty_name`: The pretty name of the callback that was executed  
__Please Note__: This is a best effort, the name of the callback may still be of little help, depending on the specific callback implementation.

## Performance impact
As many of you might be concerned about the performance impact of this library, I have run some benchmarks to measure the performance impact of this library.  
In summary the performance impact is negligible for most use cases.  
You can find the more detailed information in the following [README.md](stress_tests/results/README.md).

## Usage examples
You can find examples projects showing potential use cases in the [examples](examples) folder.  
Currently there is only the [fastapi with prometheus exporter example](examples/fastapi_with_prometheus) but more will be added in the future.


## Roadmap
- [x] Add support for the amount of `Handle`'s on the event loop
- [x] Add an examples folder
- [x] Add loop lag metric (Inspired from nodejs loop monitoring)
- [x] Add visibility into which `Handle` are making the event loop slower
- [ ] Add easier integration with `uvicorn`
- [ ] Add easier integration with popular monitoring tools like Prometheus



## Credits
* I took a lot of inspiration from the [uvloop](https://github.com/MagicStack/uvloop) project with everything
regarding the user interface of swapping the IO loop.
* The great pycon talk - https://www.youtube.com/watch?v=GSiZkP7cI80&t=16s