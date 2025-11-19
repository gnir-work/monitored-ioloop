# Monitored IO Loop Examples

Examples demonstrating `monitored_ioloop` usage, from simple scripts to production FastAPI applications with Prometheus metrics.

## Examples

### 1. Simple Python Example (`simple_python_example/`)

Basic event loop monitoring demonstrating blocking vs. non-blocking operations.

**Run:**
```bash
cd simple_python_example
uv run python simple_python_example.py
```

**What you'll see:**
- Warnings for blocking operations (`time.sleep()`) that slow down the event loop
- Loop lag warnings when tasks are delayed due to blocking operations

### 2. FastAPI with Prometheus (`fastapi_with_prometheus/`)

Example showing FastAPI integration with Prometheus metrics export.

**Run:**
```bash
cd fastapi_with_prometheus
just run  # this will start the FastAPI server with monitored event loop
just create-traffic # or: uv run python create_traffic.py # to generate some load
```

**Test endpoints:**
- http://localhost:1441/ping - Fast endpoint
- http://localhost:1441/async_slow?sleep_for=5&coroutines_number=10 - Proper async
- http://localhost:1441/blocking_slow?sleep_for=1 - Blocking operation (bad!)

**Metrics:** http://localhost:1551/metrics
- `slow_callbacks_wall_time_histogram` - Execution time of slow operations (>500ms)
- `loop_lag_time_histogram` - Scheduling delays

## Integrating with FastAPI

### Step 1: Create the monitored loop factory

```python
from monitored_ioloop.monitored_asyncio import monitored_asyncio_loop_factory
from monitored_ioloop.monitoring import IoLoopMonitorState

def monitor_callback(state: IoLoopMonitorState) -> None:
    # Your monitoring logic (log, export to Prometheus, etc.)
    if state.callback_wall_time > 0.5:
        print(f"Slow operation: {state.callback_pretty_name} took {state.callback_wall_time}s")

loop_factory = monitored_asyncio_loop_factory(monitor_callback)
```

### Step 2: Add the middleware (optional but recommended)

```python
from monitored_ioloop.helpers.fastapi import MonitoredIOLoopMiddleware
from fastapi import FastAPI

app = FastAPI()
app.add_middleware(MonitoredIOLoopMiddleware)
```

**What the middleware does:**
Sets human-readable task names for HTTP requests so your monitoring callback receives useful identifiers like `[GET] /api/users` instead of cryptic task names. It automatically masks numeric path segments (e.g., `/users/123/profile` becomes `/users/_/profile`) for better metric aggregation.

### Step 3: Run with uvicorn using the `--loop` flag

```bash
uvicorn server:app --loop server:loop_factory
```

The `--loop` flag tells uvicorn to use your monitored loop factory instead of the default event loop. This is the key to integrating monitoring into FastAPI applications.