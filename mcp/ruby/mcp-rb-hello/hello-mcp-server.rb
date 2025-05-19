require 'mcp'

name "hello-world"

version "1.0.0"

# Define a resource
resource "hello://world" do
  name "Hello World"
  description "A simple hello world message"
  call { "Hello, World!" }
end

# Define a resource template
resource_template "hello://{user_name}" do
  name "Hello User"
  description "A simple hello user message"
  call { |args| "Hello, #{args[:user_name]}!" }
end

# Define a tool
tool "greet" do
  description "Greet someone by name"
  argument :name, String, required: true, description: "Name to greet"
  call do |args|
    "Hello, #{args[:name]}!"
  end
end

# Define a tool with nested arguments
tool "greet_full_name" do
  description "Greet someone by their full name"
  argument :person, required: true, description: "Person to greet" do
    argument :first_name, String, required: false, description: "First name"
    argument :last_name, String, required: false, description: "Last name"
  end
  call do |args|
    "Hello, First: #{args[:person][:first_name]} Last: #{args[:person][:last_name]}!"
  end
end

# Define a tool with an Array argument
tool "group_greeting" do
  description "Greet multiple people at once"
  argument :people, Array, required: true, items: String, description: "People to greet"
  call do |args|
    args[:people].map { |person| "Hello, #{person}!" }.join(", ")
  end
end
