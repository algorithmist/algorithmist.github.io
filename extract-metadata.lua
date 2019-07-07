function ExtractMetadata(meta)
  -- Get the title and subtitle
  local title = pandoc.utils.stringify(meta.title)
  local subtitle = pandoc.utils.stringify(meta.subtitle)

  -- Get the filename
  local article_path = PANDOC_STATE.input_files[1]
  local article_path_components = {}
  article_path:gsub('([^/]*)/', function(c) table.insert(article_path_components, c) end)
  local article_filename = article_path_components[#article_path_components]

  -- Output in CSV to a file that the generator script will read
  -- Get the output file location
  local posts_list_filename = pandoc.utils.stringify(meta.posts_list_filename)
  local posts_list_file = io.open(posts_list_filename, 'a')
  local entry = '"' .. article_filename .. '","' .. title .. '","' .. subtitle .. '"\n'
  posts_list_file:write(entry)
  posts_list_file:close()

  -- Don't actually change anything
  return nil
end

return {
  {
    Meta = ExtractMetadata
  }
}
