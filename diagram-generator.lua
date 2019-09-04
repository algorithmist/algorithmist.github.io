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

function inline_svg(block)
  -- Shows up with --log_level=DEBUG
  -- print('---')
  -- print(dump(block))
  if block.attr.classes[1] ~= 'graphviz' then
    return nil
  end

  local svg = nil
  local caption = nil
  local animate = nil
  local fig_style = nil
  if block.attributes['source'] then
    local source = block.attributes['source']
    local metafile = io.open(source, 'r')
    local content = metafile:read("*a")
    svg = pandoc.pipe('dot', {'-Tsvg'}, content)
  end
  if block.attributes['caption'] then
    caption = block.attributes['caption']
  end
  if block.attributes['animate'] then
    animate = block.attributes['animate']
  end
  if block.attributes['fig_style'] then
    fig_style = block.attributes['fig_style']
  end

  local name = block.attr.identifier

  -- This is incredibly hacky. We should find a better way. We're only doing it
  -- because onload events do not fire for divs or figures.
  if animate then
    svg = string.gsub(svg, '<svg', '<svg onload="' .. animate .. '()"', 1)
  end

  local figObj = nil
  if fig_style then
    figObj = pandoc.RawBlock('html', '<figure style="' .. fig_style .. '">\n\t' .. svg)
  else
    figObj = pandoc.RawBlock('html', '<figure>\n\t' .. svg)
  end
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
  {CodeBlock = inline_svg},
}
