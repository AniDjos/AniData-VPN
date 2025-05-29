#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPT_DIR/venv_pyside6/bin/activate"
python "$SCRIPT_DIR/run_modern_ui.py"
