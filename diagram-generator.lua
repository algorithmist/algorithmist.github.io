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
  local animate = nil
  local name = nil
  if block.attributes["caption"] then
    caption = block.attributes['caption']
  end
  if block.attributes["animate"] then
    animate = block.attributes['animate']
  end
  if block.attributes['name'] then
    name = block.attributes['name']
  end

  -- This is incredibly hacky. We should find a better way. We're only doing it
  -- because onload events do not fire for divs or figures.
  if animate then
    svg = string.gsub(svg, '<svg', '<svg onload="' .. animate .. '()"', 1)
    print(svg)
  end

  local figObj = pandoc.RawBlock('html', '<figure>\n\t' .. svg)
  if caption then
    figObj.text = figObj.text .. '\t<figcaption>' .. caption .. '</figcaption>\n'
  end
  if animate then
    figObj.text = figObj.text .. '\t<button id="' .. animate .. '_prev" disabled="true" '
    figObj.text = figObj.text .. 'onclick="' .. animate .. '_backward()">Step backward</button>\n'
    figObj.text = figObj.text .. '\t<button id="' .. animate .. '_next" disabled="true" '
    figObj.text = figObj.text .. 'onclick="' .. animate .. '_forward()">Step forward</button>\n'
  end
  
  figObj.text = figObj.text .. '</figure>'
  local divObj = pandoc.Div(figObj)

  if name then
    divObj.attributes['name'] = name
    divObj.identifier = 'fig:' .. name
  end

  divObj.classes[#divObj.classes + 1] = 'fig'

  return divObj
end

return {
  {CodeBlock = CodeBlock},
}
