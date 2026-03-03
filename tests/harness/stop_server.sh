#!/bin/bash
set -e

if [ -z "$TEST_DIR" ]; then
    echo "ERROR: TEST_DIR environment variable is not set."
else
    if [ -f "$TEST_DIR/server.pid" ]; then
        SERVER_PID=$(cat "$TEST_DIR/server.pid")
        echo "Stopping server with PID: $SERVER_PID"
        kill -15 $SERVER_PID 2>/dev/null || true

        # Wait for the process to exit
        for i in {1..15}; do
            if ! kill -0 $SERVER_PID 2>/dev/null; then
                echo "Server stopped successfully."
                break
            fi
            sleep 1
        done

        # If it's still running, force kill
        if kill -0 $SERVER_PID 2>/dev/null; then
            echo "Server did not stop gracefully, forcing kill."
            kill -9 $SERVER_PID 2>/dev/null || true
        fi
    else
        echo "WARNING: server.pid not found in $TEST_DIR"
    fi
fi
