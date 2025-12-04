#!/bin/bash
set -e

KEYFILE="/data/replica.key"

# Generate keyfile if it doesn't exist
if [ ! -f "$KEYFILE" ]; then
    echo "Generating MongoDB keyfile at $KEYFILE..."
    # Try openssl, fall back to /dev/urandom if needed
    if command -v openssl >/dev/null 2>&1; then
        openssl rand -base64 756 > "$KEYFILE"
    else
        head -c 756 /dev/urandom | base64 > "$KEYFILE"
    fi
    
    chmod 400 "$KEYFILE"
    chown 999:999 "$KEYFILE"
fi

# Execute the command passed to this script (usually docker-entrypoint.sh ...)
exec "$@"
