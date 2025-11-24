#!/bin/bash
cd /home/kavia/workspace/code-generation/professional-portfolio-showcase-45999-46008/backend
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

