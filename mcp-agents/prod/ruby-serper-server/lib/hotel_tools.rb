# lib/hotel_tools.rb

require 'fast_mcp'
require 'google_search_results'

module HotelTools
  # Tool to search for hotels
  class SearchHotels < FastMcp::Tool
    description "Search for hotels using Serper API"
    arguments do
      required(:q).filled(:string).description("Hotel search query (e.g., 'hotels in London')")
      required(:check_in_date).filled(:string).description("Check-in date (YYYY-MM-DD)")
      required(:check_out_date).filled(:string).description("Check-out date (YYYY-MM-DD)")
      optional(:adults).filled(:integer).description("Number of adults")
      optional(:children).filled(:integer).description("Number of children")
      optional(:rooms).filled(:integer).description("Number of rooms")
      optional(:currency).filled(:string).description("Currency (e.g., USD)")
      optional(:hl).filled(:string).description("Language and country (e.g., en)")
    end

    def call(q:, check_in_date:, check_out_date:, adults: nil, children: nil, rooms: nil, currency: "USD", hl: "en")
      params = {
        api_key: ENV.fetch('SERP_API_KEY', nil),
        engine: "google_hotels",
        q: q,
        check_in_date: check_in_date,
        check_out_date: check_out_date,
        adults: adults,
        children: children,
        rooms: rooms,
        currency: currency,
        hl: hl,
      }.compact # Remove nil values
      raise('Missing ENV["SERP_API_KEY"].. failing.') unless params[:api_key]

      search = GoogleSearch.new(params)
      hash_results = search.get_hash
      # TODO: Process and format the results nicely
      hash_results.to_json
    end
  end

  # Register tools here
  # FastMcp::Server.register_tool(SearchHotels)
end
