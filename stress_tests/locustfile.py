from locust import HttpUser, task, between
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)


class FastAPIUser(HttpUser):
    host = "http://localhost:1441"
    wait_time = between(1, 2)

    @task
    def ping(self) -> None:
        self.client.get("/ping")

    @task
    def async_slow(self) -> None:
        self.client.get("/async_slow?sleep_for=5")
