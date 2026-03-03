#!/bin/bash
set -e

# Setup test environment
export REPO_DIR=$(pwd)
export TEST_DIR=$(mktemp -d)
echo "Setting up test environment in $TEST_DIR"

mkdir -p "$TEST_DIR/bin"
mkdir -p "$TEST_DIR/data"
mkdir -p "$TEST_DIR/logs"

# Ensure binary is built
if [ ! -f "$REPO_DIR/build/game" ]; then
    echo "Building game server..."
    cd "$REPO_DIR" && make -j4
fi

# Copy binary
cp "$REPO_DIR/build/game" "$TEST_DIR/bin/"

# Copy other required files (e.g. config, pem)
if [ -f "$REPO_DIR/tibia.pem" ]; then
    cp "$REPO_DIR/tibia.pem" "$TEST_DIR/bin/"
fi

# Set up test mode flag
export TIBIA_TEST_MODE=1

# Create a minimal .tibia config file to satisfy the script parser
cat << CONFIG_EOF > "$TEST_DIR/bin/.tibia"
binpath = "."
datapath = "../data"
logpath = "../logs"
mappath = "../data"
monsterpath = "../data"
savepath = "../data"
world = "Test"
CONFIG_EOF

# Start the game server
cd "$TEST_DIR/bin"
./game > "../logs/startup.log" 2>&1 &
SERVER_PID=$!
echo "$SERVER_PID" > "../server.pid"

echo "Server started with PID: $SERVER_PID"

# Wait for server to start and become ready (checking logs or port)
for i in {1..10}; do
    if grep -q "horche an Port" "../logs/startup.log" || nc -z localhost 7171 2>/dev/null; then
        echo "Server is ready."
        break
    fi
    sleep 1
done

if ! nc -z localhost 7171 2>/dev/null; then
    echo "ERROR: Server failed to start properly. Logs:"
    cat "../logs/startup.log"
    kill $SERVER_PID 2>/dev/null || true
fi

echo "Server is up and running."
cd "$REPO_DIR"
