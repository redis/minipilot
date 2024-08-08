#!/bin/sh

# Run the pre-entrypoint setup tasks
/data/entrypoint.sh

# Execute the original entrypoint command
exec /entrypoint.sh "$@"
