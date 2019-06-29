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
  local caption = nil
  if block.attributes["caption"] then
    caption = block.attributes['caption']
  end

  local figObj = pandoc.RawBlock('html', '<figure>\n\t' .. svg)
  if caption then
    figObj.text = figObj.text .. '\t<figcaption>' .. caption .. '</figcaption>\n'
  end
  
  figObj.text = figObj.text .. '</figure>'
  local divObj = pandoc.Div(figObj)

  if block.attributes['name'] then
    divObj.attributes['name'] = block.attributes['name']
    divObj.identifier = 'fig:' .. block.attributes['name']
  end

  divObj.classes[#divObj.classes + 1] = 'fig'

  return divObj
end

return {
  {CodeBlock = CodeBlock},
}
