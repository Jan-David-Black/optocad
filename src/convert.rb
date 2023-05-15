layout = RBA::Layout.new
layout.read($input)
for tc in layout.top_cells
  tc.flatten(true)
  puts(tc.name)
  if not $input.include? tc.name[0..3]
    layout.prune_cell(tc.cell_index, -1)
  end
end
lo = RBA::SaveLayoutOptions.new
lo.select_all_cells
lo.select_all_layers
lo.set_format_from_filename($output)
lo.scale_factor = 1e-3
layout.write($output, lo)
