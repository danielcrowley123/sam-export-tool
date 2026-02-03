#!/usr/bin/env python3
"""Run the SAM.gov Export Tool web UI."""

from sam_export.server import run_server

if __name__ == '__main__':
    run_server(debug=False)
