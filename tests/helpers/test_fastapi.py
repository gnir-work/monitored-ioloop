import asyncio

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from monitored_ioloop.helpers.fastapi import MonitoredIOLoopMiddleware


@pytest.fixture
def fastapi_app() -> FastAPI:
    app = FastAPI()

    @app.get("/ping")
    async def ping() -> str:
        return "ping"

    @app.get("/simple_route")
    @app.get("/nested/route")
    @app.get("/query_parameters")
    @app.get("/path/parameters/{_path_parameter}")
    @app.post("/post/method")
    async def test_route() -> str:
        if current_task := asyncio.current_task():
            return current_task.get_name()

        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="No current task."
        )

    return app


@pytest.fixture
def default_monitoring_middleware(
    fastapi_app: FastAPI,
) -> None:
    fastapi_app.add_middleware(MonitoredIOLoopMiddleware)


@pytest.fixture
def test_client(fastapi_app: FastAPI) -> TestClient:
    return TestClient(fastapi_app)


@pytest.mark.usefixtures("default_monitoring_middleware")
def test_monitored_async_io_middleware__simple_route_still_works(
    test_client: TestClient,
) -> None:
    response = test_client.get("/ping")
    assert response.status_code == 200
    assert response.json() == "ping"


@pytest.mark.usefixtures("default_monitoring_middleware")
def test_monitored_async_io_middleware__simple_routes_task_name(
    test_client: TestClient,
) -> None:
    response = test_client.get("/simple_route")
    assert response.status_code == 200
    assert response.json() == "[GET] /simple_route"


@pytest.mark.usefixtures("default_monitoring_middleware")
def test_monitored_async_io_middleware__nested_route_task_name(
    test_client: TestClient,
) -> None:
    response = test_client.get("/nested/route")
    assert response.status_code == 200
    assert response.json() == "[GET] /nested/route"


@pytest.mark.usefixtures("default_monitoring_middleware")
def test_monitored_async_io_middleware__query_parameters_task_name(
    test_client: TestClient,
) -> None:
    response = test_client.get("/query_parameters?_query=test")
    assert response.status_code == 200
    assert response.json() == "[GET] /query_parameters"


@pytest.mark.usefixtures("default_monitoring_middleware")
def test_monitored_async_io_middleware__path_parameters_task_name(
    test_client: TestClient,
) -> None:
    response = test_client.get("/path/parameters/test")
    assert response.status_code == 200, response.text
    assert response.json() == "[GET] /path/parameters/test"


@pytest.mark.usefixtures("default_monitoring_middleware")
def test_monitored_async_io_middleware__path_parameters_with_numbers_are_masked_task_name(
    test_client: TestClient,
) -> None:
    response = test_client.get("/path/parameters/1234")
    assert response.status_code == 200, response.text
    assert response.json() == "[GET] /path/parameters/_"


@pytest.mark.usefixtures("default_monitoring_middleware")
def test_monitored_async_io_middleware__post_method_task_name(
    test_client: TestClient,
) -> None:
    response = test_client.post("/post/method")
    assert response.status_code == 200, response.text
    assert response.json() == "[POST] /post/method"
