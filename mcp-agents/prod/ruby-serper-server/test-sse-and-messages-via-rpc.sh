#!/bin/bash

# This script listens to a Server-Sent Events (SSE) endpoint and sends a JSON-RPC request to the messages endpoint.
# Built 50/50 between Gemini and Riccardo.

# Output file for SSE events
SSE_OUTPUT_FILE="sse_output.log"

# Start listening to SSE endpoint in the background
# -N: Disable buffering
# --connect-timeout 5: Set connection timeout to 5 seconds
curl -N http://localhost:9292/mcp/sse --connect-timeout 5 > "$SSE_OUTPUT_FILE" &
SSE_PID=$! # Get the PID of the background curl process

echo "Listening to SSE on http://localhost:9292/mcp/sse (PID: $SSE_PID)"
echo "SSE output will be saved to $SSE_OUTPUT_FILE"

# Give the SSE listener a moment to establish connection
sleep 1

# Issue the JSON-RPC request via the messages endpoint
echo "Sending JSON-RPC request to http://localhost:9292/mcp/messages"
curl -X POST -H "Content-Type: application/json" -d '{"jsonrpc": "2.0", "id": "1", "method": "tools/list", "params": {} }' http://localhost:9292/mcp/messages

# Wait a bit for the SSE message to be received and written to the file
sleep 2

echo "Reading SSE output from $SSE_OUTPUT_FILE:"
cat "$SSE_OUTPUT_FILE"

# Clean up the background curl process
kill $SSE_PID > /dev/null 2>&1
wait $SSE_PID 2>/dev/null # Wait for the process to actually terminate

echo "Script finished."

echo "Last SSE message received has the following tools:"
cat sse_output.log  | grep "data: {" | tail -1 | cut -d' ' -f 2- | jq -r '.result.tools[] | " 🛠️ \(.name)\t➡️➡️\t\(.description)"'
#cat sse_output.log  | grep "data: {" | tail -1

# cat response-sse.json | jq -r '.result.tools[] | "\(.name) ➡️➡️ \(.description)"'
