; English engine patches. Assembled by build.py:
;   armips asm/main.asm -strequ ROM <rom> -definelabel CodeBase <addr> -definelabel KernTable <addr>
; CodeBase sits in the freed Japanese string space (within BL range of the renderer); build.py zeroes it first.
.gba
.open ROM, 0x08000000

; --- kanji-bank lookups in the glyph emitter (r5 = text object). Original: movs r0,#6; movs r1,#0xC;
;     bl 0x08000CAC (archive 6.12). Now each string brings its own bank of pre-rendered 16x16 cells.
.org 0x08032550
.thumb
    add r0, r5, #0
    bl BankForObj
    mov r8, r8
.org 0x080325F2
    add r0, r5, #0
    bl BankForObj
    mov r8, r8

; --- kern table pointer literals (both text-object inits): ED cells advance 16 px (k = 0)
.org 0x08031BEC
.word KernTable
.org 0x08031EA8
.word KernTable

; --- archive lookup 0x08000CAC(group r0, item r1) -> r0: consult OverrideTable first (rebuilt graphics)
.org 0x08000CAC
.thumb
    ldr r2, [pc, #0]            ; literal at 0x08000CB0
    bx r2
.word ArcLookup | 1

.org CodeBase
.thumb
.align 4
ArcLookup:                      ; table: u8 group, u8 item, u16 pad, u32 address; group 0xFF ends
    push {r4}
    ldr r4, =OverrideTable
@@loop:
    ldrb r2, [r4]
    cmp r2, #0xFF
    beq @@orig
    cmp r2, r0
    bne @@next
    ldrb r2, [r4, #1]
    cmp r2, r1
    bne @@next
    ldr r0, [r4, #4]
    pop {r4}
    bx lr
@@next:
    add r4, #8
    b @@loop
@@orig:                         ; original body of 0x08000CAC
    pop {r4}
    add r2, r0, #0
    ldr r0, =0x08787970
    lsl r2, r2, #2
    add r2, r2, r0
    ldr r2, [r2]
    add r0, r2, r0
    lsl r1, r1, #1
    add r1, r1, r0
    ldrh r1, [r1]
    add r0, r0, r1
    bx lr
.pool

.align 4
; r0 = text object -> r0 = bank base. Strings are 4-aligned with the bank address in the word before them.
BankForObj:
    ldr r1, [r0, #4]            ; string pointer table
    add r0, #0x38
    ldrb r0, [r0]               ; current string index
    lsl r0, r0, #2
    ldr r0, [r1, r0]            ; string start
    sub r0, #4
    ldr r0, [r0]                ; its bank
    bx lr

.close
