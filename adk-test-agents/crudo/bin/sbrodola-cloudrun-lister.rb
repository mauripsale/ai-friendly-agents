#!/usr/bin/env ruby

# --- sbrodola-cloudrun-lister.rb ---
# Desc: Finds Cloud Run services across accessible GCP projects.
# Requires: gcloud SDK installed and authenticated, Ruby installed.

require 'json'
require 'open3' # To capture stdout, stderr, and status from gcloud

# --- Configuration ---
# Add any global gcloud flags if needed (e.g., --impersonate-service-account)
# Example: GCLOUD_FLAGS = "--impersonate-service-account=your-sa@your-project.iam.gserviceaccount.com"
GCLOUD_FLAGS = "".freeze

# --- Helper Functions ---

# Get list of project IDs the current gcloud user can see
def get_accessible_project_ids
  puts "🔭 Fetching accessible project list using gcloud..."
  command = "gcloud projects list --format=\"value(projectId)\" #{GCLOUD_FLAGS}"
  stdout, stderr, status = Open3.capture3(command)

  unless status.success?
    $stderr.puts "💥 Failed to list projects! Error:"
    $stderr.puts stderr
    exit 1 # Can't proceed without projects
  end

  project_ids = stdout.lines.map(&:strip).reject(&:empty?)
  puts "✅ Found #{project_ids.count} projects."
  project_ids
end

# Get Cloud Run services for a specific project
# Returns a hash: { status: :success/:error, data: [...]/:message }
def get_cloud_run_services(project_id)
  # Using --format=json gives us structured data including the region
  # Note: This command lists services across ALL regions in the project implicitly.
  command = "gcloud run services list --project=#{project_id} --format=json #{GCLOUD_FLAGS}"
  stdout, stderr, status = Open3.capture3(command)

  if status.success?
    begin
      services_data = JSON.parse(stdout)
      # Process the data into the desired format {name: ..., region: ...}
      formatted_services = services_data.map do |service|
        name = service.dig('metadata', 'name')
        # Region is often directly in metadata in recent gcloud versions
        region = service.dig('metadata', 'region')
        # Fallback check in labels if not directly in metadata
        region ||= service.dig('metadata', 'labels', 'cloud.googleapis.com/location')

        # If we couldn't find name or region, something is odd. Log a warning.
        unless name && region
          $stderr.puts "\n⚠️ Warning: Could not extract name or region for a service in #{project_id}. Data: #{service.inspect}"
          next # Skip this malformed service entry
        end
        { name: name, region: region }
      end.compact # Remove any nils from skipped services

      return { status: :success, data: formatted_services }

    rescue JSON::ParserError => e
      # This shouldn't happen if gcloud status is success, but safety first!
      return { status: :error, message: "JSON Parse Error: #{e.message}" }
    end
  else
    # Analyze stderr for common failure reasons
    if stderr.include?("PERMISSION_DENIED") || stderr.include?("does not have permission")
      return { status: :error, message: "Insufficient permissions (run.services.list likely missing)" }
    elsif stderr.include?("run.googleapis.com is not enabled") || stderr.include?("API has not been used")
      return { status: :error, message: "Cloud Run API not enabled" }
    elsif stderr.include?("doesn't have any Cloud Run services") # Check specific gcloud message
        return { status: :success, data: [] } # Treat as success, but no services
    else
      # Catch-all for other gcloud errors
      # Limit stderr length in case it's huge
      error_snippet = stderr.strip.lines.first(5).join.strip
      return { status: :error, message: "gcloud error: #{error_snippet}..." }
    end
  end
end

# --- Main Execution ---

project_ids = get_accessible_project_ids
results = {}
total_projects = project_ids.count

puts "\n🕵️‍♀️ Scanning projects for Cloud Run services..."

project_ids.each_with_index do |project_id, index|
  # Provide some progress feedback
  print "  [#{index + 1}/#{total_projects}] Checking #{project_id}... "

  service_info = get_cloud_run_services(project_id)

  case service_info[:status]
  when :success
    if service_info[:data].empty?
      puts "🍃 No services found."
      # Add project_id with empty list to results if you want to explicitly see projects with no services.
      # results[project_id] = []
    else
      puts "☁️ Found #{service_info[:data].count} service(s)."
      results[project_id] = service_info[:data]
    end
  when :error
    puts "🚫 Error: #{service_info[:message]}"
    results[project_id] = { "error": service_info[:message] } # Structured error
  end
end

puts "\n🎉 Scan complete!"

# --- Output ---
output_file = "cloud_run_services_inventory4user.json"
puts "\n💾 Writing results to #{output_file}..."

begin
  File.write(output_file, JSON.pretty_generate(results))
  puts "✅ Success! Output saved."
rescue StandardError => e
  $stderr.puts "💥 Failed to write output file! Error: #{e.message}"
  $stderr.puts "\n📋 Raw Results:"
  puts JSON.pretty_generate(results) # Print to stdout as fallback
end
