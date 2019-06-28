function dump(o)
   if type(o) == 'table' then
      local s = '{ '
      for k,v in pairs(o) do
         if type(k) ~= 'number' then k = '"'..k..'"' end
         s = s .. '['..k..'] = ' .. dump(v) .. ','
      end
      return s .. '} '
   else
      return tostring(o)
   end
end

function CodeBlock(block)
  -- Shows up with --log_level=DEBUG
  print('---')
  print(dump(block))

  local svg = pandoc.pipe('dot', {'-Tsvg'}, block.text)

  local attrs = {}
  -- Hack to always have a space before the concatenated string.
  table.insert(attrs, '')
  if block.identifier then
    table.insert(attrs, 'id="' .. block.identifier .. '"')
  end
  if block.attributes['style'] then
    table.insert(attrs, 'style="' .. block.attributes['style'] .. '"')
  end
  --if block.attributes['width'] then
  --  table.insert(attrs, 'width="' .. block.attributes['width'] .. '"')
  --end
  --if block.attributes['height'] then
  --  table.insert(attrs, 'height="' .. block.attributes['height'] .. '"')
  --end
  table.insert(attrs, 'height="100%"')
  table.insert(attrs, 'width="100%"')

  return pandoc.RawBlock('html', '<svg' .. table.concat(attrs, ' ') .. '>' .. svg .. '</svg>')
end

return {
  {CodeBlock = CodeBlock},
}
