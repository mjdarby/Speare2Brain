#!/usr/bin/python3

########################################################################
#
#  Speare2Brain, the Shakespeare -> Brainfuck transpiler
#
#  Copyright (C) 2014 Matthew Darby
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or (at
#  your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307,
#  USA.
#
########################################################################
import sys, re

class MemoryLayout:
    """A representation of the Brainfuck memory layout offsets"""
    def __init__(self):
        self.pointer = 0
        self.copy_register_offset = 0
        self.result_register_offset = 1
        self.loop_register_offset = 2
        self.retrieve_register_offset = 3
        self.temp_register_offset = 4
        self.temp_two_register_offset = 5
        self.right_register_offset = 6
        self.on_stage_one_register_offset = 7
        self.on_stage_two_register_offset = 8
        self.active_character_register_offset = 9
        self.second_character_register_offset = 10
        self.first_character_offset = 11
        self.characters = ["left"]
        self.character_to_offset = {}
        self.left_register_counter = 0

    def add_character(self, character_name):
        self.characters.append(character_name)

    def finalise_characters(self):
        """Calculate the offsets for each character, which is a function
        of their position in the characters array"""
        for idx, character in enumerate(self.characters):
            self.character_to_offset[character] = (self.first_character_offset +
                                                   idx)

    def move_pointer_to_character(self, character_name):
        """Outputs the required Brainfuck commands to move to the
        passed character's offset"""
        try:
            offset = self.character_to_offset[character_name]
            self.pointer = offset
            return ">" * offset
        except KeyError:
            print("Error: Character does not exist: " + character_name,
                  file=sys.stderr)
            raise

    def move_pointer_to_character_stack_counter(self, character_name):
        """Outputs the required Brainfuck commands to move to the
        passed character's stack counter"""
        try:
            offset = self.character_to_offset[character_name]
            offset += len(self.characters)
            self.pointer = offset
            return ">" * offset
        except KeyError:
            print("Error: Character does not exist: " + character_name,
                  file=sys.stderr)
            raise

    def get_character_stack_position_offset(self,
                                            character_name,
                                            stack_pos):
        """Outputs the required Brainfuck commands to move to the
        passed character's stack counter"""
        try:
            offset = self.character_to_offset[character_name]
            offset += (len(self.characters) + 1) * stack_pos
            return offset
        except KeyError:
            print("Error: Character does not exist: " + character_name,
                  file=sys.stderr)
            raise

    def copy_register(self, source_register_offset, destination_register_offset):
        """Outputs the Brainfuck commands to copy a value between
        registers. Will assume Copy is empty."""
        # Move the source value to the destination and copy registers
        output_brainfuck = self.zero_value_at_offset(self.copy_register_offset)
        output_brainfuck += self.move_pointer_to_offset(source_register_offset)
        output_brainfuck += "[-" + self.reset_pointer()
        output_brainfuck += self.move_pointer_to_offset(
            destination_register_offset)
        output_brainfuck += "+" + self.reset_pointer()
        output_brainfuck += self.move_pointer_to_offset(
            self.copy_register_offset)
        output_brainfuck += "+" + self.reset_pointer()
        output_brainfuck += self.move_pointer_to_offset(
            source_register_offset) + "]"
        output_brainfuck += self.reset_pointer()
        # Copy back
        output_brainfuck += self.move_pointer_to_offset(
            self.copy_register_offset)
        output_brainfuck += "[-" + self.reset_pointer()
        output_brainfuck += self.move_pointer_to_offset(
            source_register_offset)
        output_brainfuck += "+" + self.reset_pointer()
        output_brainfuck += self.move_pointer_to_offset(
            self.copy_register_offset) + "]"
        output_brainfuck += self.reset_pointer()
        return output_brainfuck

    def copy_from_second_character_register(self,
                                            destination_register_offset):
        """Copies the content of the second characters's register into
        a destination register via addition. Assumes Copy will be zero.
        Same for Loop."""
        copy_function = lambda source, dest: self.copy_register(dest, source)
        output_brainfuck = self.copy_second_character_skeleton(
            destination_register_offset,
            copy_function)

        return output_brainfuck

    def copy_from_first_character_register(self,
                                            destination_register_offset):
        """Copies the content of the active characters's register into
        a destination register via addition. Assumes Copy will be zero.
        Same for Loop."""
        copy_function = lambda source, dest: self.copy_register(dest, source)
        output_brainfuck = self.copy_first_character_skeleton(
            destination_register_offset,
            copy_function)

        return output_brainfuck

    def copy_into_second_character_register(self,
                                            source_register_offset):
        """Copies the content of the source register into
        the second characters's register via addition. Assumes Copy will
        be zero. Same for Loop."""
        copy_function = lambda source, dest: self.copy_register(source, dest)
        output_brainfuck = self.copy_second_character_skeleton(
            source_register_offset,
            copy_function)

        return output_brainfuck

    def output_second_character_register(self):
        """Outputs the content of the source register"""
        copy_function = lambda source, dest: (
            self.move_pointer_to_offset(dest) + "." + self.reset_pointer())
        output_brainfuck = self.copy_second_character_skeleton(
            0,
            copy_function)

        return output_brainfuck

    def reset_second_character_register(self):
        """Resets the content of the source register"""
        copy_function = lambda source, dest: (
            self.move_pointer_to_offset(dest) + "[-]" + self.reset_pointer())
        output_brainfuck = self.copy_second_character_skeleton(
            0,
            copy_function)

        return output_brainfuck

    def copy_second_character_skeleton(self,
                                       register,
                                       copy_function):
        return self.copy_character_skeleton(
            register,
            copy_function,
            self.second_character_register_offset)

    def copy_first_character_skeleton(self,
                                       register,
                                       copy_function):
        return self.copy_character_skeleton(
            register,
            copy_function,
            self.active_character_register_offset)

    def copy_character_skeleton(self,
                                register,
                                copy_function,
                                character_register):
        """Provides the skeleton code for copying into/from the second
        character"""
        retrieve_register_offset = self.retrieve_register_offset
        loop_register_offset = self.loop_register_offset

        output_brainfuck = ""
        # Setup our Copy and Loop registers, Loop will be made zero
        # once we enter the inner loop
        output_brainfuck += self.copy_register(
            character_register,
            self.retrieve_register_offset)
        output_brainfuck += self.add_value_at_offset(
            1,
            self.loop_register_offset)
        output_brainfuck += self.move_pointer_to_offset(retrieve_register_offset)

        inner_brainfuck = ""
        for character in self.characters[::-1]:
            # Relies off the first character in the array holding the
            # first position in memory, etc.
            temp_brainfuck = ""
            temp_brainfuck += "[-" + inner_brainfuck
            temp_brainfuck += "<" * retrieve_register_offset
            self.pointer = 0 # Ick.
            # The first time we reach here, it's because we either hit
            # the bottom bottom or skipped an inner loop.
            temp_brainfuck += self.move_pointer_to_offset(loop_register_offset)
            temp_brainfuck += "[-" # If this is the first time in, decrement Loop
            temp_brainfuck += self.reset_pointer()
            temp_brainfuck += copy_function(
                register,
                self.character_to_offset[character])
            temp_brainfuck += self.move_pointer_to_offset(loop_register_offset)
            temp_brainfuck += "]"
            temp_brainfuck += self.reset_pointer()
            temp_brainfuck += self.move_pointer_to_offset(retrieve_register_offset)
            temp_brainfuck += "]"
            inner_brainfuck = temp_brainfuck
            self.pointer = 0 # Hacks! HACKS
        output_brainfuck += inner_brainfuck + "<" * retrieve_register_offset
        return output_brainfuck

    def move_pointer_to_offset(self, offset):
        """Outputs the required Brainfuck commands to move to the
        passed raw offset"""
        self.pointer = offset
        return ">" * offset

    def zero_value_at_offset(self, offset):
        """Outputs the Brainfuck commands to zero the value at a given
        offset and reset the pointer."""
        output_brainfuck = ""
        output_brainfuck += self.move_pointer_to_offset(offset)
        output_brainfuck += "[-]"
        output_brainfuck += self.reset_pointer()
        return output_brainfuck

    def add_value_at_offset(self, value, offset):
        """Outputs the Brainfuck commands to zero the value at a given
        offset and reset the pointer."""
        output_brainfuck = ""
        output_brainfuck += self.move_pointer_to_offset(offset)
        output_brainfuck += "+" * value
        output_brainfuck += self.reset_pointer()
        return output_brainfuck

    def subtract_value_at_offset(self, value, offset):
        """Outputs the Brainfuck commands to zero the value at a given
        offset and reset the pointer."""
        output_brainfuck = ""
        output_brainfuck += self.move_pointer_to_offset(offset)
        output_brainfuck += "-" * value
        output_brainfuck += self.reset_pointer()
        return output_brainfuck

    def reset_pointer(self):
        """Returns the Brainfuck command required to move the pointer
        back to the 0 position. Needs to be called after you are
        finished manipulating the memory location you're currently at"""
        offset = self.pointer
        self.pointer = 0
        return "<" * offset

def parse_file(file_text, memory):
    output_brainfuck = ""
    tokens = file_text.split(',')
    idx = 0
    # The main loop for parsing finds valid tokens and runs the
    # the associated functions. Each function returns how many
    # tokens we should skip after we've finished processing.
    while idx < len(tokens):
        current_token = tokens[idx]
        if current_token in token_function_map().keys():
            bf, off = token_function_map()[current_token](tokens, memory, idx)
            output_brainfuck += bf
            idx += off
        else:
            idx += 1
    return output_brainfuck

def setup_memory_offsets(tokens, memory, offset):
    """Extract the character array which resides between the chars and
    endchars tokens"""
    character_array = extract_elements_between_tokens(
        tokens,
        token_pairs()["chars"],
        offset)
    if not character_array:
        raise Exception("No characters found in input NSPL file, aborting")
    for character in character_array:
        memory.add_character(character)
    memory.finalise_characters()
    return ["", 2 + len(character_array)]

def enter_characters(tokens, memory, offset):
    """Returns the Brainfuck required to load the given characters into
    the character registers"""
    output_brainfuck = ""
    character_array = extract_elements_between_tokens(
        tokens,
        token_pairs()["enter_scene_multiple"],
        offset)
    if not character_array:
        raise Exception("No characters provided to put onto scene, aborting")
    if len(character_array) != 2:
        raise Exception("Wrong number of characters provided")
    stage_offset = memory.on_stage_one_register_offset
    for character in character_array:
        # Move to the OS1 + OS2 registers, wipe out the current value if
        # necessary and replace them with the index of the new characters
        # on stage
        output_brainfuck += memory.move_pointer_to_offset(stage_offset)
        output_brainfuck += "[-]"
        output_brainfuck += "+" * (memory.characters.index(character) + 1)
        output_brainfuck += memory.reset_pointer()
        stage_offset += 1
    return [output_brainfuck, 2 + len(character_array)]

def exit_characters(tokens, memory, offset):
    """Returns the Brainfuck required to remove all characters
    from the character registers"""
    output_brainfuck = ""
    character_array = extract_elements_between_tokens(
        tokens,
        token_pairs()["exit_scene_multiple"],
        offset)
    if not (len(character_array) == 2 or len(character_array) == 0):
        raise Exception("Wrong number of characters provided")
    stage_offset = memory.on_stage_one_register_offset
    # Move to the OS1 + OS2 registers, wipe out the current value if
    # necessary and replace them with the index of the new characters
    # on stage
    output_brainfuck += memory.move_pointer_to_offset(stage_offset)
    output_brainfuck += "[-]"
    output_brainfuck += memory.reset_pointer()
    stage_offset += 1
    output_brainfuck += memory.move_pointer_to_offset(stage_offset)
    output_brainfuck += "[-]"
    output_brainfuck += memory.reset_pointer()
    return [output_brainfuck, 2 + len(character_array)]

def enter_character(tokens, memory, offset):
    """Returns the Brainfuck required to load the given character into
    the empty character register"""
    output_brainfuck = ""
    new_character = extract_next_elements(tokens, 2, offset)[1]
    new_character_offset = memory.characters.index(new_character) + 1
    stage_offset = memory.on_stage_one_register_offset
    result_register_offset = memory.result_register_offset
    copy_register_offset = memory.copy_register_offset
    loop_register_offset = memory.loop_register_offset

    # There must be at least one empty space for the character to join.
    # We'll assume that if it isn't OS1, it must be OS2.
    # Reset result
    output_brainfuck += memory.move_pointer_to_offset(result_register_offset)
    output_brainfuck += "[-]"
    output_brainfuck += memory.reset_pointer()

    # If OS1 == 0, fill it with the character and set Result to 1
    # Idiom for 'if equal to 0:
    #  <set non-zero register to 1><test register>
    #  [<set not-zero register to 0>]<test non-zero register>[<code>]
    output_brainfuck += memory.move_pointer_to_offset(result_register_offset)
    output_brainfuck += "+" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(stage_offset)
    output_brainfuck += "[" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(result_register_offset)
    output_brainfuck += "-" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        stage_offset)
    # Escape loop with Loop trick
    output_brainfuck += "[-" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        loop_register_offset)
    output_brainfuck += "+" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        stage_offset)
    output_brainfuck += "]" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        stage_offset)
    output_brainfuck += "]" + memory.reset_pointer()

    # Restore OS1
    output_brainfuck += memory.move_pointer_to_offset(
        loop_register_offset)
    output_brainfuck += "[-" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        stage_offset)
    output_brainfuck += "+" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        loop_register_offset)
    output_brainfuck += "]" + memory.reset_pointer()

    # If Result is not zero, OS1 is empty and needs to be filled
    # Use the copy register to keep track of the fact we entered this loop
    # If copy is zero, don't copy into OS2 instead
    output_brainfuck += memory.move_pointer_to_offset(copy_register_offset)
    output_brainfuck += "[-]+" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(result_register_offset)
    output_brainfuck += "[" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(stage_offset)
    output_brainfuck += "+" * new_character_offset + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(copy_register_offset)
    output_brainfuck += "-" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(result_register_offset)
    output_brainfuck += "-]" + memory.reset_pointer()

    # If the above didn't execute, Copy contains 1.
    stage_offset += 1
    output_brainfuck += memory.move_pointer_to_offset(copy_register_offset)
    output_brainfuck += "[" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(stage_offset)
    output_brainfuck += "+" * new_character_offset + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(copy_register_offset)
    output_brainfuck += "-]" + memory.reset_pointer()

    # Final result: Copy 0, Result 0, OS1 or OS2 filled with new offset
    return [output_brainfuck, 2]

def exit_character(tokens, memory, offset):
    """Returns the Brainfuck required to remove the given character from
    the stage."""
    output_brainfuck = ""
    character = extract_next_elements(tokens, 2, offset)[1]
    character_offset = memory.characters.index(character) + 1
    stage_one_offset = memory.on_stage_one_register_offset
    stage_two_offset = memory.on_stage_two_register_offset
    loop_register_offset = memory.loop_register_offset

    # We'll first try and remove the character from OS1
    # If there's still a non-zero value in OS1, we will
    # restore OS1 and delete OS2 instead.
    output_brainfuck += memory.subtract_value_at_offset(character_offset,
                                                        stage_one_offset)
    output_brainfuck += memory.move_pointer_to_offset(stage_one_offset)
    output_brainfuck += "[" + memory.reset_pointer()
    output_brainfuck += memory.subtract_value_at_offset(character_offset,
                                                        stage_two_offset)
    output_brainfuck += memory.add_value_at_offset(character_offset,
                                                   stage_one_offset)
    output_brainfuck += memory.move_pointer_to_offset(stage_one_offset)
    output_brainfuck += "[-" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(loop_register_offset)
    output_brainfuck += "+" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(stage_one_offset)
    output_brainfuck += "]" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(stage_one_offset)
    output_brainfuck += "]" + memory.reset_pointer()

    # Restore OS1
    output_brainfuck += memory.move_pointer_to_offset(
        loop_register_offset)
    output_brainfuck += "[-" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(stage_one_offset)
    output_brainfuck += "+" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        loop_register_offset)
    output_brainfuck += "]" + memory.reset_pointer()


    # Final result: Copy 0, Result 0, OS1 or OS2 filled with new offset
    return [output_brainfuck, 2]

def activate_character(tokens, memory, offset):
    """Returns the brainfuck for moving the given character into the
    active character register, also moving the other character into the
    second person register if present"""
    output_brainfuck = ""
    active_character = extract_next_elements(tokens, 2, offset)[1]
    active_character_offset = memory.characters.index(active_character) + 1
    result_register_offset = memory.result_register_offset
    active_character_register_offset = memory.active_character_register_offset
    second_character_register_offset = memory.second_character_register_offset
    os1_register_offset = memory.on_stage_one_register_offset
    os2_register_offset = memory.on_stage_two_register_offset
    copy_register_offset = memory.copy_register_offset
    loop_register_offset = memory.loop_register_offset
    # We'll trust that this actor is on stage, but we need to find the
    # offset of the other actor on stage. This means checking if
    # the first on-stage offset is equal to the active character's
    # offset. If not, copy in the secnd on-stage offset instead.

    # Reset the active character and result
    output_brainfuck += memory.move_pointer_to_offset(result_register_offset)
    output_brainfuck += "[-]"
    output_brainfuck += memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        active_character_register_offset)
    output_brainfuck += "[-]"
    output_brainfuck += memory.reset_pointer()

    # Put the target active character into the result and
    # active character slots.
    output_brainfuck += memory.move_pointer_to_offset(result_register_offset)
    output_brainfuck += "+" * active_character_offset
    output_brainfuck += memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        active_character_register_offset)
    output_brainfuck += "+" * active_character_offset
    output_brainfuck += memory.reset_pointer()

    # Subtract Result from OS2, put the result in Result
    # Sub-step: OS2 goes into copy register while subtracting
    output_brainfuck +=  memory.move_pointer_to_offset(os2_register_offset)
    output_brainfuck += "[-" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(result_register_offset)
    output_brainfuck += "-" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(copy_register_offset)
    output_brainfuck += "+" + memory.reset_pointer()
    output_brainfuck +=  memory.move_pointer_to_offset(os2_register_offset)
    output_brainfuck += "]" + memory.reset_pointer()
    # Sub-step: Restore OS2
    output_brainfuck +=  memory.move_pointer_to_offset(copy_register_offset)
    output_brainfuck += "[-" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(os2_register_offset)
    output_brainfuck += "+" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(copy_register_offset)
    output_brainfuck += "]" + memory.reset_pointer()

    # Set Sec to 0. If Result != 0, add 1 to Sec. Reset Result.
    output_brainfuck += memory.move_pointer_to_offset(
        second_character_register_offset)
    output_brainfuck += "[-]" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(result_register_offset)
    output_brainfuck += "[" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        second_character_register_offset)
    output_brainfuck += "+" + memory.reset_pointer()
    # Reset result.
    output_brainfuck += memory.move_pointer_to_offset(result_register_offset)
    output_brainfuck += "[-]"
    output_brainfuck += "]" + memory.reset_pointer()


    # If Sec != 0, copy OS2 into Result
    output_brainfuck += memory.move_pointer_to_offset(
        second_character_register_offset)
    output_brainfuck += "[" + memory.reset_pointer()
    # Sub-step: OS2 goes into copy register while adding
    output_brainfuck +=  memory.move_pointer_to_offset(os2_register_offset)
    output_brainfuck += "[-" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(result_register_offset)
    output_brainfuck += "+" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(copy_register_offset)
    output_brainfuck += "+" + memory.reset_pointer()
    output_brainfuck +=  memory.move_pointer_to_offset(os2_register_offset)
    output_brainfuck += "]" + memory.reset_pointer()
    # Sub-step: Restore OS2
    output_brainfuck +=  memory.move_pointer_to_offset(copy_register_offset)
    output_brainfuck += "[-" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(os2_register_offset)
    output_brainfuck += "+" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(copy_register_offset)
    output_brainfuck += "]" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        loop_register_offset)
    output_brainfuck += "+" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        second_character_register_offset)
    output_brainfuck += "-"
    output_brainfuck += "]" + memory.reset_pointer()

    # Restore Sec from Loop
    output_brainfuck +=  memory.move_pointer_to_offset(loop_register_offset)
    output_brainfuck += "[-" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        second_character_register_offset)
    output_brainfuck += "+" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(loop_register_offset)
    output_brainfuck += "]" + memory.reset_pointer()

    # Sec - 1
    output_brainfuck += memory.move_pointer_to_offset(
        second_character_register_offset)
    output_brainfuck += "-" + memory.reset_pointer()

    # If Sec != 0, reset sec, copy OS1 into Sec
    output_brainfuck += memory.move_pointer_to_offset(
        second_character_register_offset)
    output_brainfuck += "[[-]" + memory.reset_pointer()
    # Sub-step: OS1 goes into copy register while adding to Sec
    output_brainfuck +=  memory.move_pointer_to_offset(os1_register_offset)
    output_brainfuck += "[-" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        second_character_register_offset)
    output_brainfuck += "+" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(copy_register_offset)
    output_brainfuck += "+" + memory.reset_pointer()
    output_brainfuck +=  memory.move_pointer_to_offset(os1_register_offset)
    output_brainfuck += "]" + memory.reset_pointer()
    # Sub-step: Restore OS1
    output_brainfuck +=  memory.move_pointer_to_offset(copy_register_offset)
    output_brainfuck += "[-" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(os1_register_offset)
    output_brainfuck += "+" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(copy_register_offset)
    output_brainfuck += "]" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        second_character_register_offset)
    output_brainfuck += "[-" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        loop_register_offset)
    output_brainfuck += "+" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        second_character_register_offset)
    output_brainfuck += "]" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        second_character_register_offset)
    output_brainfuck += "]" + memory.reset_pointer()

    # Restore Sec
    output_brainfuck += memory.move_pointer_to_offset(
        loop_register_offset)
    output_brainfuck += "[-" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        second_character_register_offset)
    output_brainfuck += "+" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        loop_register_offset)
    output_brainfuck += "]" + memory.reset_pointer()

    # Add result to Sec.
    # Sub-step: Result goes into copy register while adding to Sec
    output_brainfuck +=  memory.move_pointer_to_offset(result_register_offset)
    output_brainfuck += "[-" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        second_character_register_offset)
    output_brainfuck += "+" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(copy_register_offset)
    output_brainfuck += "+" + memory.reset_pointer()
    output_brainfuck +=  memory.move_pointer_to_offset(result_register_offset)
    output_brainfuck += "]" + memory.reset_pointer()
    # Sub-step: Restore OS1
    output_brainfuck +=  memory.move_pointer_to_offset(copy_register_offset)
    output_brainfuck += "[-" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(result_register_offset)
    output_brainfuck += "+" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(copy_register_offset)
    output_brainfuck += "]" + memory.reset_pointer()

    # Reset result
    output_brainfuck += memory.move_pointer_to_offset(result_register_offset)
    output_brainfuck += "[-]" + memory.reset_pointer()
    return [output_brainfuck, 2]

def output_character(tokens, memory, offset):
    """Returns the brainfuck for outputing in ASCII the value in the
    Second character's register"""
    output_brainfuck = memory.output_second_character_register()
    return [output_brainfuck, 1]

def breakpoint(tokens, memory, offset):
    """Returns the brainfuck for entering a debug state in some
    BF interpreters"""
    output_brainfuck = "#"
    return [output_brainfuck, 1]

def assign(tokens, memory, offset):
    """Returns the brainfuck for resetting the Result register before
    evaluating the internal expressions and assigning the result
    to the character referenced in the Second register."""
    expression_array = extract_elements_between_tokens(
        tokens,
        token_pairs()["assign"],
        offset)
    output_brainfuck = ""
    output_brainfuck += memory.zero_value_at_offset(
        memory.result_register_offset)
    # Do the expression evaluation, not fun..
    output_brainfuck += evaluate_expression(memory.result_register_offset,
                                            tokens,
                                            memory,
                                            offset+1)[0]

    # Put Result into the Second character's register after resetting
    output_brainfuck += memory.reset_second_character_register()
    output_brainfuck += memory.copy_into_second_character_register(
        memory.result_register_offset)
    return [output_brainfuck, len(expression_array) + 2]

# Binary and unary functions will destroy Left and Right during
# processing
def add_expression(target_register, memory):
    left_register_offset = memory.get_character_stack_position_offset(
        "left",
        memory.left_register_counter)
    # Add Right to Left and jam it in the target register
    output_brainfuck = ""
    output_brainfuck += memory.move_pointer_to_offset(
        memory.right_register_offset)
    output_brainfuck += "[-" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        left_register_offset)
    output_brainfuck += "+" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        memory.right_register_offset)
    output_brainfuck += "]" + memory.reset_pointer()
    output_brainfuck += memory.copy_register(left_register_offset,
                                             target_register)
    return output_brainfuck

def sub_expression(target_register, memory):
    left_register_offset = memory.get_character_stack_position_offset(
        "left",
        memory.left_register_counter)
    # Subtract Right from Left and jam it in the target register
    output_brainfuck = ""
    output_brainfuck += memory.move_pointer_to_offset(
        memory.right_register_offset)
    output_brainfuck += "[-" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        left_register_offset)
    output_brainfuck += "-" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        memory.right_register_offset)
    output_brainfuck += "]" + memory.reset_pointer()
    output_brainfuck += memory.copy_register(left_register_offset,
                                             target_register)
    return output_brainfuck

def mul_expression(target_register, memory):
    left_register_offset = memory.get_character_stack_position_offset(
        "left",
        memory.left_register_counter)
    # Keep copying Left into Target until Loop runs out
    output_brainfuck = ""
    output_brainfuck += memory.move_pointer_to_offset(
        memory.right_register_offset)
    output_brainfuck += "[-" + memory.reset_pointer()
    output_brainfuck += memory.copy_register(left_register_offset,
                                             target_register)
    output_brainfuck += memory.move_pointer_to_offset(
        memory.right_register_offset)
    output_brainfuck += "]" + memory.reset_pointer()
    return output_brainfuck

def mod_expression(target_register, memory):
    output_brainfuck = ""
    return output_brainfuck

def div_expression(target_register, memory):
    left_register_offset = memory.get_character_stack_position_offset(
        "left",
        memory.left_register_counter)
    output_brainfuck = ""
    # Counter
    output_brainfuck += memory.zero_value_at_offset(memory.temp_register_offset)
    # Loop needs to be zeroed
    output_brainfuck += memory.zero_value_at_offset(
        memory.loop_register_offset)

    # Loop over Left until left_zero is set
    output_brainfuck += memory.move_pointer_to_offset(left_register_offset)
    output_brainfuck += "[" + memory.reset_pointer()
    output_brainfuck += memory.zero_value_at_offset(
        memory.retrieve_register_offset)
    output_brainfuck += memory.copy_register(memory.right_register_offset,
                                             memory.loop_register_offset)
    output_brainfuck += memory.move_pointer_to_offset(
        memory.loop_register_offset)
    output_brainfuck += "[" + memory.reset_pointer()
    output_brainfuck += memory.subtract_value_at_offset(
        1,
        memory.loop_register_offset)
    output_brainfuck += memory.subtract_value_at_offset(1,
                                                        left_register_offset)
    output_brainfuck += memory.move_pointer_to_offset(left_register_offset)
    output_brainfuck += "[" + memory.reset_pointer()
    output_brainfuck += memory.add_value_at_offset(
        1,
        memory.retrieve_register_offset)
    output_brainfuck += memory.move_pointer_to_offset(left_register_offset)
    output_brainfuck += "[-" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        memory.copy_register_offset)
    output_brainfuck += "+" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(left_register_offset)
    output_brainfuck += "]" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(left_register_offset)
    output_brainfuck += "]" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        memory.copy_register_offset)
    output_brainfuck += "[-" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(left_register_offset)
    output_brainfuck += "+" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        memory.copy_register_offset)
    output_brainfuck += "]" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        memory.loop_register_offset)
    output_brainfuck += "]" + memory.reset_pointer()

    # Check if Right is equal to Retrieve. If not, left = 0.
    # If so, counter + 1
    output_brainfuck += memory.copy_register(memory.right_register_offset,
                                             memory.loop_register_offset)
    output_brainfuck += memory.move_pointer_to_offset(
        memory.retrieve_register_offset)
    output_brainfuck += "[-" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        memory.loop_register_offset)
    output_brainfuck += "-" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        memory.retrieve_register_offset)
    output_brainfuck += "]" + memory.reset_pointer()

    # Test Loop and wipe out left if true
    output_brainfuck += memory.move_pointer_to_offset(
        memory.loop_register_offset)
    output_brainfuck += "[-" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        left_register_offset)
    output_brainfuck += "[-]" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        memory.loop_register_offset)
    output_brainfuck += "]" + memory.reset_pointer()

    # If left isn't zero, we didn't nuke it, so add one to the counter
    output_brainfuck += memory.move_pointer_to_offset(left_register_offset)
    output_brainfuck += "[" + memory.reset_pointer()
    output_brainfuck += memory.add_value_at_offset(
        1,
        memory.temp_register_offset)
    output_brainfuck += memory.move_pointer_to_offset(left_register_offset)
    output_brainfuck += "[-" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        memory.copy_register_offset)
    output_brainfuck += "+" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(left_register_offset)
    output_brainfuck += "]" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(left_register_offset)
    output_brainfuck += "]" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        memory.copy_register_offset)
    output_brainfuck += "[-" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(left_register_offset)
    output_brainfuck += "+" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        memory.copy_register_offset)
    output_brainfuck += "]" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        left_register_offset)
    output_brainfuck += "]" + memory.reset_pointer()
    output_brainfuck += memory.copy_register(memory.temp_register_offset,
                                             target_register)
    # Cleanup
    output_brainfuck += memory.zero_value_at_offset(
        memory.temp_register_offset)
    output_brainfuck += memory.zero_value_at_offset(
        memory.loop_register_offset)
    output_brainfuck += memory.zero_value_at_offset(
        memory.retrieve_register_offset)
    return output_brainfuck

def cube_expression(target_register, memory):
    temp_register_offset = memory.temp_register_offset
    output_brainfuck = ""
    output_brainfuck += memory.zero_value_at_offset(
        memory.loop_register_offset)
    output_brainfuck += memory.zero_value_at_offset(
        memory.temp_register_offset)
    output_brainfuck += memory.copy_register(memory.right_register_offset,
                                             memory.loop_register_offset)
    output_brainfuck += memory.move_pointer_to_offset(
        memory.right_register_offset)
    output_brainfuck += "[-" + memory.reset_pointer()
    output_brainfuck += memory.copy_register(memory.loop_register_offset,
                                             temp_register_offset)
    output_brainfuck += memory.move_pointer_to_offset(
        memory.right_register_offset)
    output_brainfuck += "]" + memory.reset_pointer()
    output_brainfuck += memory.copy_register(temp_register_offset,
                                             memory.retrieve_register_offset)
    output_brainfuck += memory.zero_value_at_offset(temp_register_offset)
    output_brainfuck += memory.copy_register(memory.loop_register_offset,
                                             memory.right_register_offset)
    output_brainfuck += memory.move_pointer_to_offset(
        memory.right_register_offset)
    output_brainfuck += "[-" + memory.reset_pointer()
    output_brainfuck += memory.copy_register(memory.retrieve_register_offset,
                                             temp_register_offset)
    output_brainfuck += memory.move_pointer_to_offset(
        memory.right_register_offset)
    output_brainfuck += "]" + memory.reset_pointer()
    output_brainfuck += memory.zero_value_at_offset(
        memory.retrieve_register_offset)
    output_brainfuck += memory.zero_value_at_offset(
        memory.loop_register_offset)
    output_brainfuck += memory.copy_register(temp_register_offset,
                                             target_register)
    output_brainfuck += memory.zero_value_at_offset(
        memory.temp_register_offset)
    return output_brainfuck

def factorial_expression(target_register, memory):
    output_brainfuck = ""
    return output_brainfuck

def square_expression(target_register, memory):
    temp_register_offset = memory.temp_register_offset
    # Keep copy Right into Loop and use Loop like Right in the Mul
    # function
    output_brainfuck = ""
    output_brainfuck += memory.zero_value_at_offset(
        memory.loop_register_offset)
    output_brainfuck += memory.zero_value_at_offset(
        memory.temp_register_offset)
    output_brainfuck += memory.copy_register(memory.right_register_offset,
                                             memory.loop_register_offset)
    output_brainfuck += memory.move_pointer_to_offset(
        memory.right_register_offset)
    output_brainfuck += "[-" + memory.reset_pointer()
    output_brainfuck += memory.copy_register(memory.loop_register_offset,
                                             temp_register_offset)
    output_brainfuck += memory.move_pointer_to_offset(
        memory.right_register_offset)
    output_brainfuck += "]" + memory.reset_pointer()
    output_brainfuck += memory.zero_value_at_offset(
        memory.loop_register_offset)
    output_brainfuck += memory.copy_register(temp_register_offset,
                                             target_register)
    output_brainfuck += memory.zero_value_at_offset(
        temp_register_offset)
    return output_brainfuck

def sqrt_expression(target_register, memory):
    output_brainfuck = ""
    return output_brainfuck

def twice_expression(target_register, memory):
    # Keep copying Left into Target until Loop runs out
    output_brainfuck = ""
    output_brainfuck += memory.move_pointer_to_offset(
        memory.right_register_offset)
    output_brainfuck += memory.zero_value_at_offset(
        memory.temp_register_offset)
    output_brainfuck += memory.move_pointer_to_offset(
        memory.right_register_offset)
    output_brainfuck += "[-" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        memory.temp_register_offset)
    output_brainfuck += "++" + memory.reset_pointer()
    output_brainfuck += memory.move_pointer_to_offset(
        memory.right_register_offset)
    output_brainfuck += "]" + memory.reset_pointer()
    output_brainfuck += memory.copy_register(memory.temp_register_offset,
                                             target_register)
    output_brainfuck += memory.zero_value_at_offset(
        memory.temp_register_offset)
    return output_brainfuck

def value_of_expression(target_register,
                        tokens,
                        memory,
                        offset):
    character = extract_next_elements(tokens, 2, offset)[1]
    output_brainfuck = ""
    if character == "second_person":
        output_brainfuck += memory.copy_from_second_character_register(
            target_register)
    elif character == "first_person":
        output_brainfuck += memory.copy_from_first_character_register(
            target_register)
    else:
        character_register = memory.character_to_offset[character]
        output_brainfuck += memory.copy_register(character_register,
                                                target_register)
    return output_brainfuck
def const_expression(target_register,
                     tokens,
                     memory,
                     offset):
    value = int(extract_next_elements(tokens, 2, offset)[1])
    sign = "+" if value > 0 else "-"
    value = value if value > 0 else -value
    output_brainfuck = ""
    output_brainfuck += memory.move_pointer_to_offset(target_register)
    output_brainfuck += sign * value
    output_brainfuck += memory.reset_pointer()
    return output_brainfuck

def evaluate_expression(target_register, tokens, memory, offset):
    """Returns the brainfuck for evaluating an expression and moving
    the result into Result."""
    output_brainfuck = ""
    # We need to figure out which order we have to evaluate the
    # expressions in to avoid clobbering any values.
    # For binary operations, we can load each argument into a register
    # but this gets hard if each argument is a binary operation itself.
    # We'll use a third register to hold one of the results if necessary.

    # Pluck off the top token and evaluate its arguments and slam them
    # into the Left/Right/Spare register if necessary
    expression = tokens[offset]
    new_offset = 0
    if expression in binary_expression_function_map().keys():
        # Figure out if both arguments are binary expressions themselves
        # and if so, use Left and Spare (if argument is left arg) or
        # Right and Spare (if argument is right arg) and then copy
        # the value
        output_brainfuck, new_offset = evaluate_binary_expression(
            target_register,
            tokens,
            memory,
            offset+1)
        # At this point, all the required nested calculations are done
        # and the Left Right registers are correctly populated. Do the
        # calculation and put it where it's meant to go
        output_brainfuck += binary_expression_function_map()[expression](
            target_register,
            memory)

    elif expression in unary_expression_function_map().keys():
        output_brainfuck, new_offset = evaluate_unary_expression(target_register,
                                                                 tokens,
                                                                 memory,
                                                                 offset+1)
        output_brainfuck += unary_expression_function_map()[expression](
            target_register,
            memory)

    elif expression in terminal_function_map().keys():
        new_offset = offset + 2
        output_brainfuck += terminal_function_map()[expression](
            target_register,
            tokens,
            memory,
            offset)
    else:
        print(expression)
        print(tokens[offset-5:offset+5])
        raise Exception("Expression not found.")

    return [output_brainfuck, new_offset]

def evaluate_binary_expression(target_register,
                               tokens,
                               memory,
                               offset):
    output_brainfuck = ""
    left_register_offset = memory.get_character_stack_position_offset(
        "left",
        memory.left_register_counter)
    output_brainfuck += memory.zero_value_at_offset(left_register_offset)
    output_brainfuck += memory.zero_value_at_offset(memory.right_register_offset)
    memory.left_register_counter += 1
    left_brainfuck, right_offset = evaluate_expression(
        left_register_offset,
        tokens,
        memory,
        offset)
    right_brainfuck, end_offset = evaluate_expression(
        memory.right_register_offset,
        tokens,
        memory,
        right_offset)
    output_brainfuck += left_brainfuck + right_brainfuck
    memory.left_register_counter -= 1
    return [output_brainfuck, end_offset + 1]

def evaluate_unary_expression(target_register,
                              tokens,
                              memory,
                              offset):
    output_brainfuck = ""
    output_brainfuck += memory.zero_value_at_offset(memory.right_register_offset)
    eval_brainfuck, new_offset = evaluate_expression(
        memory.right_register_offset,
        tokens,
        memory,
        offset)
    output_brainfuck += eval_brainfuck
    return [output_brainfuck, new_offset+1]

def extract_next_elements(tokens, number_of_elements, offset):
    """Starting from the offset element of the tokens array, extract the
    next N elements."""
    return tokens[offset:offset + number_of_elements]

def extract_elements_between_tokens(tokens, token_pair, offset):
    """Starting from the offset element of the tokens array, find all
    elements between the first occurrence of the start token and the
    first occurrence of the end token."""
    elements = []
    start_token, end_token = token_pair[0], token_pair[1]
    empty_exp = start_token + "," + end_token
    reg_exp = start_token + ",(.*?)," + end_token

    string_to_search = ",".join(tokens[offset:])
    empty_match = re.match(empty_exp, string_to_search)
    if empty_match:
        return []

    reg_match = re.match(reg_exp, string_to_search)
    if reg_match:
        elements = reg_match.group(1)
        elements = elements.split(",")
    else:
        elements = []
    return elements

def token_function_map():
    function_map = {"chars": setup_memory_offsets,
                    "enter_scene_multiple": enter_characters,
                    "exit_scene_multiple": exit_characters,
                    "enter_scene": enter_character,
                    "exit_scene": exit_character,
                    "activate": activate_character,
                    "assign": assign,
                    "output": output_character,
                    "break": breakpoint}
    return function_map

def token_pairs():
    pairs_map = {"chars": ["chars", "endchars"],
                 "enter_scene_multiple": ["enter_scene_multiple",
                                          "end_enter_scene_multiple"],
                 "exit_scene_multiple": ["exit_scene_multiple",
                                         "end_exit_scene_multiple"],
                 "assign": ["assign",
                            "end_assign"]}
    return pairs_map

def binary_expression_function_map():
    function_map = {"add": add_expression,
                    "sub": sub_expression,
                    "mul": mul_expression,
                    "mod": mod_expression,
                    "div": div_expression}
    return function_map

def binary_expression_pairs():
    pairs_map = {"add": ["add", "end_add"],
                 "sub": ["sub", "end_sub"],
                 "mul": ["mul", "end_mul"],
                 "mod": ["mod", "end_mod"],
                 "div": ["div", "end_div"]}
    return pairs_map

def unary_expression_function_map():
    function_map = {"cube": cube_expression,
                    "factorial": factorial_expression,
                    "square": square_expression,
                    "sqrt": sqrt_expression,
                    "twice": twice_expression}
    return function_map

def terminal_function_map():
    function_map = {"value_of": value_of_expression,
                    "const": const_expression}
    return function_map

def tidy_up(brainfuck):
    """Removes adjacent <>"""
    def balance(match):
        string = match.group(0)
        while len(string) > 1 and string[0] != string[-1]:
            string = string[1:-1]
        return string
    brainfuck = re.sub('<+>+', balance, brainfuck)
    brainfuck = re.sub('>+<+', balance, brainfuck)
    return brainfuck

if __name__ == "__main__":
    mem = MemoryLayout()
    if len(sys.argv) < 2:
        print("Usage: ./nspl2bf.py input.nspl > output.bf")
        sys.exit(2)
    filename = sys.argv[1]
    try:
        f = open(filename, "r")
    except IOError:
        print("Could not find file " + filename, file=sys.stderr)
        sys.exit(2)
    text = f.read()
    text = re.sub('\n', '', text)
    text = re.sub(', *$', '', text)
    f.close()

    brainfuck = parse_file(text, mem)
    brainfuck = tidy_up(brainfuck)
    print(brainfuck)
