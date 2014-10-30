Conversion to Not-Shakespeare-Programming-Language
==================================================
We're going to tear out all this 'C' garbage that spl2c produces and replace the whole thing with a far, far easier to parse alternative that I have dubbed 'Not-Shakespeare-Programming-Language', or NSPL.

NSPL is SPL but without any of the art, emotion, or fun. It only exists because I'm not brave enough to try and transpile directly to Brainfuck (read: not brave enough to do anything substantial in C).

Once compiled to NSPL, another program called nspl2bf is responsible for converting our fantastic kind-of language to Brainfuck. This document describes what nspl2bf does when it encounters each NSPL token.

Memory layout
=============
First, a quick summary of how we're going to layout the memory in the eventual Brainfuck program, where `n` is the number of characters in the source SPL program. We'll use C array notation, with `*p` being a pointer to the beginning of our memory space. Each register has a short name that I use to refer to it. It's easier to refer to the inactive on stage character as the 'second' character, and I very rarely reference the actual second character's register, so yeah.

    p[0] - Copy Register (Copy)
    p[1] - Result Register (Result)
    p[2] - Loop Termination Register (Loop)
    p[3] - On Stage 1 Register (OS1)
    p[4] - On Stage 2 Register (OS2)
    p[5] - Active Character Register (Active)
    p[6] - Inactive Character Register (Second)
    p[7] - First Character Register (First character's register)
    p[8] - Second Character Register (Second character's register)
    ...
    p[7+n] - First Character's Stack Counter
    p[8+n] - Second Character's Stack Counter
    ...
    p[7+2n] - First Character's Bottom of the Stack
    p[8+2n] - Second Character's Bottom of the Stack

Registers
=========
Each register has a particular use case, but sometimes they will be co-opted for other uses because we happen to know that it won't in use ahead of time.

* Copy - In BF, the simplest way of moving an unknown-until-runtime value from one cell to another (that I've discovered) involves looping on the source cell; decrementing the value of that cell, moving to the destination cell, incrementing that cell, then moving the pointer back to the source. In this fashion, the source cell will be emptied and the destination cell will gain the value that the source cell originally held. However, this destroys the source cell. The Copy register allows for copies between cells by not only incrementing the value of the destination cell inside the loop, but also that of the Copy register. Once the source cell is emptied, we move the value in the Copy register back into the source cell. This performs a true copy.

* Result - Multiple uses, but one notable use inside nspl2bf is as an indicator for `if-else` statements. We set the result register to 1 before moving the pointer to another register and attempting to enter one of two blocks, only one of which we want to execute. If we enter the block successfully, we immediately decrement the Result register. After we leave the block, we test Result and only enter the block if it is still non-zero; that is to say, we did not enter the first block.

* Loop - In nspl2bf, it is very important that the pointer is not moved manually. You use functions in the MemoryLayout class to return movement commands, do your BF magic, then reset the pointer. However, this puts a constraint on where the pointer must be at the end of a `[]` block: It has to be at the same place as it would have been if the block wasn't entered at all, otherwise we won't know how many `<` commands are needed to reset the pointer. This means we have a problem if we need to terminate the loop but we know that the value in the register we used to enter the loop won't necessarily be zero. To get around this, we use the Loop register: Move the value of the 'entering' register into Loop, move the pointer to said 'entering' register, allow the loop to terminate, and then move Loop back into the original register.

* On Stage (OS1, OS2) - The On Stage registers contain the memory offsets of the characters currently on stage. They're necessary because when we 'activate' an On Stage character, we need to put the inactive character into the Second register. To do this, we need to know which characters are on stage, hence the OS registers.

* Active - Not strictly necessary (as far as I can tell), this holds the offset of the active on stage character.

* Second - Holds the offset of the character that is on stage but NOT active. This is very useful, because many commands like `assign` operate on the inactive character. Having their offset stored simplifies things, but actually accessing the value at the offset will be a huge pain regardless (we do not have the luxury of knowing who inactive character at a particular instruction is at compile time, except in the most simple of programs).

* Character registers + stacks - These hold the value that each character currently, well, holds. Each character has a stack coutner cell `n` cells after their initial offset. The next cell `n` spaces after marks the bottom of the character's stack, and every `n`th space after that is another possible value of their stack.

Operations
==========
All operations and parameters are comma-delimited, and are ordered in the same way as their corresponding C transpiled equivalents. They are mostly intended to come in pairs, with any arguments existing between the two bookend tokens. Unary operations exist also. These do not have a corresponding end delimiter.

`chars, [character_list], endchars` - All tokens between chars and endchars are considered character names. Each character will be assigned an offset starting from 2. The gap between the character's offset and his stack pointer is `n`, where `n` is the number of characters in the program. There is another gap of `n` data elements between the stack pointer and each of the character's stack frames.

`actlabel, act, [act_number], endactlabel` - Defines an Act level jump point. GOTO is complicated in BF, so we'll come back to this later.

`scenelabel, act, [act_number], scene, [scene_number], endscenelabel` - Defines a Scene level jump point.

`enter_scene_multiple, [characters], end_enter_scene_multiple` - Moves two characters into the character registers. Must receive two arguments.

`exit_scene_multiple, [characters] or [], end_exit_scene_multiple` - Removes all characters from the stage, but must receive two or zero arguments to stay consistent with the original SPL.

`enter_scene, [character]` - Moves the character's offset into OS1 if OS1 is empty, otherwise clobbers OS2 with the offset instead.

`exit_scene, [character]` - Sets OS1 to 0 if equal to the given character's offset, otherwise wipes out OS2.

`activate, [character]` - Moves the given character's offset into the Active register. If the offset is equal to OS1, OS2 is copied into the Second register. Otherwise, OS1 is copied into the Second register instead.