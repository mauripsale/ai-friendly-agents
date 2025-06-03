#!/bin/bash

if [ ! -d ".venv" ] ; then ./install.sh ; fi

source .venv/bin/activate
adk web --reload --log_level debug  
