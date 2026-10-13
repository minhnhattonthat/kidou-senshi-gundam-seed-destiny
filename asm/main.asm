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

.org CodeBase
.thumb
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
