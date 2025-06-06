# Ruby Serper MCP Server

This is a simple Ruby MCP server that uses the Serper API to search Google Flights and Google Hotels.

## Available Tools

### FlightTools

*   **SearchOneWay**: Search for one-way flights using Serper API.
    *   Arguments:
        *   `departure_id` (**required**, string): Departure airport ID (e.g., ZRH)
        *   **`arrival_id`** (string): Arrival airport ID (e.g., AMS)
        *   `outbound_date` (**required**, string): Outbound date (YYYY-MM-DD)
        *   `adults` (optional, integer): Number of adults
        *   `currency` (optional, string): Currency (e.g., USD)
        *   `hl` (optional, string): Language and country (e.g., en)

*   **SearchTwoWays**: Search for two-way flights using Serper API.
    *   Arguments:
        *   `departure_id` (required, string): Departure airport ID (e.g., ZRH)
        *   `arrival_id` (required, string): Arrival airport ID (e.g., AMS)
        *   `outbound_date` (required, string): Outbound date (YYYY-MM-DD)
        *   `return_date` (required, string): Return date (YYYY-MM-DD)
        *   `adults` (optional, integer): Number of adults
        *   `currency` (optional, string): Currency (e.g., USD)
        *   `hl` (optional, string): Language and country (e.g., en)

### HotelTools

*   **SearchHotels**: Search for hotels using Serper API.
    *   Arguments:
        *   `q` (required, string): Hotel search query (e.g., 'hotels in London')
        *   `check_in_date` (required, string): Check-in date (YYYY-MM-DD)
        *   `check_out_date` (**required**): Check-out date (YYYY-MM-DD)
        *   `adults` (optional, integer): Number of adults
        *   `children` (*optional*): Number of children
        *   `rooms` (*optional*): Number of rooms
        *   `currency` (optional, string): Currency (e.g., USD)
        *   `hl` (optional, string): Language and country (e.g., en)

## How to Invoke

1.  Make sure you have the `SERP_API_KEY` environment variable set with your Serper API key.
2.  Run the server using the `justfile` command:

    ```bash
    just rack-server
    ```

    This will start the server on port 9292.

## How to Test

You can test the server using the `justfile` command:

```bash
just test-server
```

This command sends a `tools/list` request to the server and prints the available tools.
