-- Log ROM data reads (not code fetches) in frames FROM..TO: "f<frame> pc=<pc> addr=<addr> val=<v>", one line per
-- distinct (pc, addr). Find which tables a screen reads.  --var FROM=60 --var TO=64 [--var LO=0x08000000 --var HI=0x087FFFFF]
local from, to = FROM or 0, TO or 1e9
local seen, n = {}, 0
L.on_read(LO or 0x08000000, HI or 0x087FFFFF, function(addr, v)
  if L.frame < from or L.frame > to or n > 20000 then return end
  local pc = L.pc()
  if ROMPC and (pc < 0x08000000 or pc > 0x09FFFFFF) then return end  -- skip IWRAM decompressors/copies
  local k = pc * 0x10000000 + addr
  if seen[k] then return end
  seen[k] = true
  n = n + 1
  L.log(string.format("f%d pc=%08X addr=%08X val=%X", L.frame, pc, addr, v or 0))
end)
