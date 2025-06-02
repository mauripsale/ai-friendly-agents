#!/bin/bash

python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt


cat << 'EOF'

Don't forget to run the follwing command before starting ADK

source .venv/bin/activate

# then (with optional flags)
adk web --reload --log_level info
EOF