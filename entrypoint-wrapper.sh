#!/bin/sh
set -e

# Default environment variables (can be overridden at runtime)
: "${UID:=1000}"
: "${GID:=1000}"
: "${COLLECTION_ROOT:=/data/collections/collection-root}"
: "${SHARED_ROOT:=}"   # empty -> skip symlink creation

echo "[entrypoint] Checking for shared collections..."

if [ -n "$SHARED_ROOT" ] && [ -d "$SHARED_ROOT" ]; then
    echo "[entrypoint] Running create_symlinks.py as ${UID}:${GID} ..."
    # Run the script as the configured UID/GID so symlinks are created with correct ownership
    su-exec ${UID}:${GID} python3 /usr/local/bin/create_symlinks.py || {
        echo "[entrypoint] create_symlinks.py failed (non-fatal). Continuing startup."
    }
else
    echo "[entrypoint] No SHARED_ROOT provided or directory missing. Skipping symlink creation."
fi

echo "[entrypoint] Starting Radicale..."
# If no CMD provided, start Radicale with the same working invocation you used
if [ $# -eq 0 ]; then
    exec /usr/local/bin/docker-entrypoint.sh /venv/bin/radicale --config /config/config
else
    exec /usr/local/bin/docker-entrypoint.sh "$@"
fi
