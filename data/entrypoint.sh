#!/bin/sh

# Mount the local file to /tmp/dump.rdb
if [ -f /tmp/dump.rdb ]; then
    echo "Found /tmp/dump.rdb"
else
    echo "Error: /tmp/dump.rdb not found!"
    exit 1
fi

# Check if /data/dump.rdb exists
if [ ! -f /data/dump.rdb ]; then
    echo "Copying /tmp/dump.rdb to /data/dump.rdb"
    cp /tmp/dump.rdb /data/dump.rdb
else
    echo "/data/dump.rdb already exists. Skipping copy."
fi

# Execute the main command
exec "$@"
exec /entrypoint.sh "$@"