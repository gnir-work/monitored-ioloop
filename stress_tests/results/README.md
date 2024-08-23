## Stress test results
### Conditions
The stress tests were run a M1 macbook pro 2022 32GB RAM and 10 cores.
The architecture of system tests was
* 1 fastapi server running uvicorn with 1 worker
* 4 locust workers running on the same machine

### Tests
#### 300 active locust users
Under the stress of 300 users which resulted in ~70 requests __per second__ there was
no visible difference in the response time between monitored and vanilla loops.

#### 1000 active locust users
Under the stress of 1000 users which resulted in ~220 requests __per second__ there was
a 5~7% increase in response time when observing the 90th - 100th percentile of longest requests.  
requests under the 90th percentile were not affected by the monitoring loop.
