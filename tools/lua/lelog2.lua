-- Log every call of the IWRAM Le decoder 0x03005C10 (r0 = data after the 6-byte header, r1 = dest, r2 = size).
L.on_exec(0x03005C10, 0x03005C10, function()
  local s = emu.getState()
  L.log(string.format("f%d le src=%08X dst=%08X n=%X lr=%08X", L.frame, s["cpu.r0"] - 6, s["cpu.r1"], s["cpu.r2"],
    s["cpu.r14"]))
end)
