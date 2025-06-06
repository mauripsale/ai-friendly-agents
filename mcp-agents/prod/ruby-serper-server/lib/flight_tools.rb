# lib/flight_tools.rb

require 'fast_mcp'
require 'google_search_results'

module FlightTools
  # Tool to search for one-way flights
  class SearchOneWay < FastMcp::Tool
    description "Search for one-way flights using Serper API"
    arguments do
      required(:departure_id).filled(:string).description("Departure airport ID (e.g., ZRH)")
      required(:arrival_id).filled(:string).description("Arrival airport ID (e.g., AMS)")
      required(:outbound_date).filled(:string).description("Outbound date (YYYY-MM-DD)")
      optional(:adults).filled(:integer).description("Number of adults")
      optional(:currency).filled(:string).description("Currency (e.g., USD)")
      optional(:hl).filled(:string).description("Language and country (e.g., en)")
    end

    def call(departure_id:, arrival_id:, outbound_date:, adults: 1, currency: "USD", hl: "en")
      params = {
        api_key: ENV.fetch('SERP_API_KEY', nil),
        engine: "google_flights",
        departure_id: departure_id,
        arrival_id: arrival_id,
        outbound_date: outbound_date,
        adults: adults,
        currency: currency,
        hl: hl,
      }
      raise('Missing ENV["SERP_API_KEY"].. failing.') unless params[:api_key]

      search = GoogleSearch.new(params)
      hash_results = search.get_hash
      # TODO: Process and format the results nicely
      hash_results.to_json
    end
  end

  # Tool to search for two-way flights
  class SearchTwoWays < FastMcp::Tool
    description "Search for two-way flights using Serper API"
    arguments do
      required(:departure_id).filled(:string).description("Departure airport ID (e.g., ZRH)")
      required(:arrival_id).filled(:string).description("Arrival airport ID (e.g., AMS)")
      required(:outbound_date).filled(:string).description("Outbound date (YYYY-MM-DD)")
      required(:return_date).filled(:string).description("Return date (YYYY-MM-DD)")
      optional(:adults).filled(:integer).description("Number of adults")
      optional(:currency).filled(:string).description("Currency (e.g., USD)")
      optional(:hl).filled(:string).description("Language and country (e.g., en)")
    end

    def call(departure_id:, arrival_id:, outbound_date:, return_date:, adults: 1, currency: "USD", hl: "en")
      params = {
        api_key: ENV.fetch('SERP_API_KEY', nil),
        engine: "google_flights",
        departure_id: departure_id,
        arrival_id: arrival_id,
        outbound_date: outbound_date,
        return_date: return_date,
        adults: adults,
        currency: currency,
        hl: hl,
      }
      raise('Missing ENV["SERP_API_KEY"].. failing.') unless params[:api_key]

      search = GoogleSearch.new(params)
      hash_results = search.get_hash
      # TODO: Process and format the results nicely
      hash_results.to_json
    end
  end
end
