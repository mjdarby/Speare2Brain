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
        self.on_stage_one_register_offset = 2
        self.on_stage_two_register_offset = 3
        self.active_character_register_offset = 4
        self.second_character_register_offset = 5
        self.first_character_offset = 6
        self.characters = []
        self.character_to_offset = {}

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
            idx += token_function_map()[current_token](tokens, memory, idx)
        else:
            idx += 1
    return tokens

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
    return 2 + len(character_array)

def extract_elements_between_tokens(tokens, token_pair, offset):
    """Starting from the offset element of the tokens array, find all
    elements between the first occurrence of the start token and the
    first occurrence of the end token."""
    elements = []
    start_token, end_token = token_pair[0], token_pair[1]
    reg_exp = start_token + ",(.*?)," + end_token

    string_to_search = ",".join(tokens[offset:])
    reg_match = re.match(reg_exp, string_to_search)
    if reg_match:
        elements = reg_match.group(1)
    return elements.split(",")

def token_function_map():
    function_map = {"chars": setup_memory_offsets}
    return function_map

def token_pairs():
    pairs_map = {"chars": ["chars", "endchars"]}
    return pairs_map

if __name__ == "__main__":
    mem = MemoryLayout()
    if len(sys.argv) < 2:
        print("Usage: ./brain2speare.py input.b > output.spl")
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

    tokens = parse_file(text, mem)
