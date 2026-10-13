-- At the OAM builder's frame lookup (0x030062F0: ldrb r3,[sl,#2]) log each distinct sprite object (sl) with its
-- first 32 bytes. --var FROM/TO frames. Use to find the object that shows a given frame index (byte 2).
local from, to = FROM or 0, TO or 1e9
local seen = {}
L.on_exec(0x030062F0, 0x030062F0, function()
  if L.frame < from or L.frame > to then return end
  local s = emu.getState()
  local sl = s["cpu.r10"]
  if seen[sl] then return end
  seen[sl] = true
  local t = {}
  for i = 0, 31 do t[#t + 1] = string.format("%02X", emu.read(sl + i, emu.memType.gbaMemory)) end
  L.log(string.format("f%d obj=%08X %s", L.frame, sl, table.concat(t, " ")))
end)
