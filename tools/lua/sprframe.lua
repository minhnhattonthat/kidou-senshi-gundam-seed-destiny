-- Log the sprite-frame record pointer (r6) used by the IWRAM OAM builder (0x03006264) for each distinct record,
-- with the record's 8 bytes. Finds where composed sprites (mission text, logos) are defined.
--   --var FROM=60 --var TO=80
local from, to = FROM or 0, TO or 1e9
local seen = {}
L.on_exec(0x03006264, 0x03006264, function()
  if L.frame < from or L.frame > to then return end
  local s = emu.getState()
  local r6 = s["cpu.r6"]
  if seen[r6] then return end
  seen[r6] = true
  local t = {}
  for i = 0, 7 do t[#t + 1] = string.format("%02X", emu.read(r6 + i, emu.memType.gbaMemory)) end
  L.log(string.format("f%d rec=%08X %s", L.frame, r6, table.concat(t, " ")))
end)
