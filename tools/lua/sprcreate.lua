-- Log calls of the sprite-object create routine 0x08000CFC: r0-r3, 3 stack args, lr. --var FROM/TO
local from, to = FROM or 0, TO or 1e9
L.on_exec(0x08000CFC, 0x08000CFC, function()
  if L.frame < from or L.frame > to then return end
  local s = emu.getState()
  local sp = s["cpu.r13"]
  local function w(a) return emu.read(a, emu.memType.gbaMemory) | emu.read(a + 1, emu.memType.gbaMemory) << 8
    | emu.read(a + 2, emu.memType.gbaMemory) << 16 | emu.read(a + 3, emu.memType.gbaMemory) << 24 end
  L.log(string.format("f%d r0=%X r1=%X r2=%X r3=%X s0=%X s1=%X s2=%X lr=%08X", L.frame, s["cpu.r0"], s["cpu.r1"],
    s["cpu.r2"], s["cpu.r3"], w(sp), w(sp + 4), w(sp + 8), s["cpu.r14"]))
end)
