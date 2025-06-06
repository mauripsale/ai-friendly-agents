
# Ruby SDK Example STDIO/SSE Server

This directory contains example server implementations using the Model Context Protocol Ruby SDK from https://github.com/modelcontextprotocol/ruby-sdk/

*   ✅ **STDIO Server (`stdio_server.rb`)**: This example works! 🎉
    *   **How to run:** `bundle exec ruby stdio_server.rb`
    *   **How to use:** Send JSON-RPC 2.0 messages to the server's standard input. For example, to list tools, send: `{"jsonrpc": "2.0", "id": "1", "method": "tools/list", "params": {}}`

*   🔴 **SSE Server (`sse_server.rb`)**: This example currently does **NOT** work. 🐛
    *   **Command:** `bundle exec ruby sse_server.rb`
    *   **Error:** `uninitialized constant ModelContextProtocol::Transports::SseServer (NameError)`
    *   **Reason:** The `SseServer` class seems to be missing from the version of the SDK code in `../ruby-sdk-copy`. We cannot fix this example without the complete SDK code including the SSE transport implementation.
    *   **Expected Port (if it worked):** Based on external examples, an SSE server would likely run on port **8931**. 🔌

---

**Emoji Key:**

✅: Works!
🔴: Broken
🐛: Bug present
🎉: Success!
🔌: Port information
