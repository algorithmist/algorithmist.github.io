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
  -- print('---')
  -- print(dump(block))
  local svg = pandoc.pipe('dot', {'-Tsvg'}, block.text)

  return pandoc.RawBlock('html', svg)
end

return {
  {CodeBlock = CodeBlock},
}
