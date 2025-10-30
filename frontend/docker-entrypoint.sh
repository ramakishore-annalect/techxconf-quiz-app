#!/bin/sh
set -e

# Check if node_modules is empty or doesn't have vite
if [ ! -d "node_modules/vite" ]; then
    echo "Installing node modules..."
    npm install
fi

# Execute the main command
exec "$@"
