-- Log every Le decompression (ROM caller 0x08001A84): frame, source block, destination, return address.
--   emu.py ... --script tools/lua/lelog.lua
L.on_exec(0x08001A84, 0x08001A84, function()
  local s = emu.getState()
  L.log(string.format("f%d le src=%08X dst=%08X lr=%08X", L.frame, s["cpu.r0"], s["cpu.r1"], s["cpu.r14"]))
end)
