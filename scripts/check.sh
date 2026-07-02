#!/usr/bin/env bash
set -e

echo "Running Check Script..."

if command -v pytest &> /dev/null
then
    echo "Running pytest..."
    pytest
else
    echo "[Skipped] pytest not found. Project might not be fully initialized."
fi

echo "Check passed (or skipped due to missing tools)."
