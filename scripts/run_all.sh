#!/usr/bin/env bash
# Current reviewer workflow; historical pipelines live in immutable baseline archives.
set -euo pipefail
cd "$(dirname "$0")/.."
scripts/reviewer.sh build
scripts/reviewer.sh test
scripts/reviewer.sh reference
