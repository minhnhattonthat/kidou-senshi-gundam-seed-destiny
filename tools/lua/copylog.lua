-- Log every call of the IWRAM block copies (0x03006820 = 32-byte, 0x030067FC = 64-byte loops) and the BIOS
-- CpuSet/CpuFastSet SWIs that write into VRAM_LO..VRAM_HI: frame, source, dest, count, caller (lr).
--   emu.py ... --script tools/lua/copylog.lua [--var VRAM_LO=0x06010000 --var VRAM_HI=0x06017FFF]
local lo, hi = VRAM_LO or 0x06010000, VRAM_HI or 0x06017FFF
local function log(tag)
  local s = emu.getState()
  local dst = s["cpu.r1"]
  if dst >= lo and dst <= hi then
    L.log(string.format("f%d %s src=%08X dst=%08X n=%X lr=%08X", L.frame, tag, s["cpu.r0"], dst, s["cpu.r2"], s["cpu.r14"]))
  end
end
L.on_exec(0x03006820, 0x03006820, function() log("cp32") end)
L.on_exec(0x030067FC, 0x030067FC, function() log("cp64") end)
L.on_exec(0x00000B4C, 0x00000B4C, function() log("cpuset") end)
L.on_exec(0x00000BC4, 0x00000BC4, function() log("fastset") end)
