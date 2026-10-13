-- Pin a 16-bit value every frame from POKE_FROM on: --var POKE_ADDR=0x... --var POKE_VAL=0 [--var POKE_FROM=60]
-- Mesen GBA. Used to end fights fast (opponent HP) for reaching win-quote screens.
local addr, val, from = assert(POKE_ADDR, "set POKE_ADDR"), POKE_VAL or 0, POKE_FROM or 60
L.on_frame(function(f)
  if f >= from then
    emu.write(addr, val & 0xFF, emu.memType.gbaMemory)
    emu.write(addr + 1, (val >> 8) & 0xFF, emu.memType.gbaMemory)
  end
end)
