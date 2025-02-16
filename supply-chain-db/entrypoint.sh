#!/bin/bash
set -e  # Exit on error

echo "Creating symbolic link for AGE extension..."
ln -sf /usr/lib/postgresql/16/lib/age.so /usr/lib/postgresql/16/lib/plugins/age.so
echo "Symbolic link created."

echo "Starting PostgreSQL..."
exec docker-entrypoint.sh "$@"  # Call the original entrypoint
