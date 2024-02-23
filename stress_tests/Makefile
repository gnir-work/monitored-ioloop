IO_LOOP_TYPE = asyncio
OUTPUT_FILE =


run-server:
	poetry run python server/server.py --monitor-type ${IO_LOOP_TYPE}

run-stress-test:
# check if OUTPUT_FILE is defined
ifndef OUTPUT_FILE
	$(error OUTPUT_FILE is not defined)
endif
	poetry run locust --users 500 --spawn-rate 100 -t 15 --headless --process 4 --html ${OUTPUT_FILE}