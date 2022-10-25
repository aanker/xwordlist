module Jekyll
  module CommitFilter
    def commit(input)
      puts "https://github.com/aanker/xwordlist/commit/#{input}"
    end
  end
end

Liquid::Template.register_filter(Jekyll::CommitFilter)