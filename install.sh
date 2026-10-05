#!/bin/sh
# Copyright 2026 Phillip Dougherty. SPDX-License-Identifier: Apache-2.0
set -eu
foundry_python=python3
if ! command -v python3 >/dev/null 2>&1 || ! python3 -c 'import sys; sys.exit(sys.version_info < (3, 10))'; then
    foundry_install_tools=false
    foundry_dry_run=false
    for foundry_arg in "$@"; do
        case "$foundry_arg" in
            --install-tools) foundry_install_tools=true ;;
            --dry-run) foundry_dry_run=true ;;
        esac
    done
    if "$foundry_install_tools" && ! "$foundry_dry_run" && command -v brew >/dev/null 2>&1; then
        brew install python
        foundry_python="$(brew --prefix)/bin/python3"
    else
        echo "Python 3.10+ is required. Install it from python.org or with brew install python." >&2
        exit 1
    fi
fi
exec "$foundry_python" "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)/scripts/setup.py" install "$@"
