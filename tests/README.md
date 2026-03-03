# Tibia Test Harness

This directory contains a behavior-locking test harness for the Tibia 7.7 Game Server. The primary goal is to ensure no functional changes are introduced unintentionally. Every pull request must pass these tests in CI.

## Directory Structure

* `harness/`: Contains scripts to start and stop the server in a temporary environment.
    * `run_server.sh`: Linux script to compile, copy files, write a minimal config, start the server in the background, and wait for it to become ready.
    * `run_server.ps1`: Windows equivalent.
    * `stop_server.sh`: Stops the server cleanly and captures exit codes/artifacts.
* `scenarios/`: Contains black-box networking scenarios.
    * `run_scenarios.py`: Runs connect/disconnect tests, minimal handshakes, and invalid packet fuzzing to generate a `trace.json` artifact.
* `compare.py`: Compares normalized target logs and network traces against the baseline golden files, and prints a diff on failure.
* `golden/`: Canonical outputs (logs, traces) representing the correct expected behavior.

## How to run the tests locally (Linux)

To generate new target logs and traces, and compare them to the golden baseline:

```bash
# 1. Start the server (sets TEST_DIR in your environment)
source tests/harness/run_server.sh

# 2. Run scenarios to generate traces
python3 tests/scenarios/run_scenarios.py "$TEST_DIR/logs"

# 3. Stop the server gracefully
source tests/harness/stop_server.sh

# 4. Compare results
python3 tests/compare.py tests/golden/linux "$TEST_DIR/logs"
```

## Updating the Baseline

If a change modifies a log message or behavior deliberately (e.g., translating a string), the CI will fail until the golden files are updated. To update the golden files, simply copy the successful test run artifacts into the `golden/linux/` directory:

```bash
cp "$TEST_DIR/logs/startup.log" tests/golden/linux/
cp "$TEST_DIR/logs/trace.json" tests/golden/linux/
```
