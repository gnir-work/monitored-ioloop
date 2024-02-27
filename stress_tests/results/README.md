## Stress test results
### Conditions
The stress tests were run a M1 macbook pro 2022 32GB RAM and 10 cores.

### Parameters
The stress tests were measured on a fastapi server ran by uvicorn with one worker.
The stress tests library used was `locust` with the following parameters:
* 250 new users pers seconds (until maximum of 1000 users)
* 15 seconds of test duration

### Results summary
Both for `uvloop` and `asyncio` you can expect the following under heavy load (200+ request/second):
* until the 80th percentile (inclusive) there is no significant difference in the response time between monitored and vanilla loops.
* after the 90th percentile (inclusive) you can expect a 5-10% increase in response time for monitored loops.