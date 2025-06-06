
set -x

find . -type f \( -name '*.md' -o -name 'justfile' -o -name '*.py' \) -not -path './.venv/lib/python3.11/site-packages/*' -not -name 'GEMINI.md' -exec grep -HnE 'mcp-prod-agents|mcp-test-agents' {} +
