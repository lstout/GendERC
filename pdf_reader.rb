require 'pdf/reader'

reader = PDF::Reader.new(ARGV.first)

reader.pages.each do |page|
  puts page.text
end