Conversion to Not-Shakespeare-Programming-Language
==================================================
We're going to tear out all this 'C' garbage that spl2c produces and replace the whole thing with a far, far easier to parse alternative that I have dubbed 'Not-Shakespeare-Programming-Language', or NSPL.

NSPL is SPL but without any of the art, emotion, or fun. It only exists because I'm not brave enough to try and transpile directly to Brainfuck (read: not brave enough to do anything substantial in C).

Once compiled to NSPL, another program called nspl2bf is responsible for converting our fantastic kind-of language to Brainfuck. This document describes what nspl2bf does when it encounters each NSPL token.

Memory layout
=============
First, a quick summary of how we're going to layout the memory in the eventual Brainfuck program, where n is the number of characters in the source SPL program

    [0: Copy register][1: Result register][2: First character][3: Second character]...[n+2: First character stack pointer][n+3: Second character stack pointer]...[2n+2: Bottom of stack for first character]

and the memory continues such that for the `y`th bottom-most element for character `x`'s stack is stored at memory location `((y+1)*n + x + 2)`, because `(n + x + 2)` holds the stack pointer for character `x` and we need to offset all the memory by 2. The top of a character's stack is located at `n * value of stack pointer + character offset`

Operations
==========
All operations and parameters are comma-delimited, and are ordered in the same way as their corresponding C transpiled equivalents. They are mostly intended to come in pairs, with any arguments existing between the two bookend tokens. Unary operations exist also. These do not have a corresponding end delimiter.

`chars, [character_list], endchars` - All tokens between chars and endchars are considered character names. Each character will be assigned an offset starting from 2. The gap between the character's offset and his stack pointer is `n`, where `n` is the number of characters in the program. There is another gap of `n` data elements between the stack pointer and each of the character's stack frames.

actlabel, act, [act_number], endactlabel - Defines an Act level jump point. GOTO is complicated in BF, so we'll come back to this later.

scenelabel, act, [act_number], scene, [scene_number], endscenelabel - Defines a Scene level jump point.

enter_scene_multiple, [characters], end_enter_scene_multiple - Moves two characters into the character registers
