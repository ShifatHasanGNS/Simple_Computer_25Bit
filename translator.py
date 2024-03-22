# Author: Md. Shifat Hasan (2107067)

import sys

OpCodes = ['noop', 'set', 'clr', 'not', 'neg', 'and', 'or', 'xor', 'add', 'sub', 'mul', 'div', 'shl', 'shr', 'cmp', 'jmp', 'jmpz', 'jmpl', 'jmpg', 'ina', 'inx', 'outa', 'outx', 'showf', 'show', 'hlt']

UnaryOpCodes = ['noop', 'not', 'neg', 'shl', 'shr', 'showf', 'hlt']

BinaryOpCodes = ['set', 'clr', 'and', 'or', 'xor', 'add', 'sub', 'mul', 'div', 'cmp', 'jmp', 'jmpz', 'jmpl', 'jmpg', 'ina', 'inx', 'outa', 'outx', 'show']


def opcode_hex_value(opcode: str):
  id = OpCodes.index(opcode)
  id = hex(id)[2:].zfill(2)
  return id


def content_from_lines(lines: list) -> str:
  content = ''
  for line in lines:
    content += line + '\n'
  return content[:-1]


def preprocess(source_file: str) -> str:
  with open(source_file, 'r') as file:
    lines = file.readlines()

    # get lowercase version of the whole content
    lines = [line.lower() for line in lines]

    # add newline after the labels (@Label:)
    lines = [line.replace(':', ':\n') for line in lines]

    # remove spaces from the beginning and end of each line
    lines = [line.strip() for line in lines]

    # remove from '#' to '\n'
    # remove '\n' from the end of each line
    # remove empty lines
    lines = [line.split('!')[0].strip() for line in lines if line.strip() != '']

    # remove empty lines
    lines = [line for line in lines if line != '']

    return content_from_lines(lines)


def vars_and_instructions(content: str) -> tuple:
  lines = content.split('\n')
  vars = list()
  labels = dict()
  instructions = list()

  for line in lines:
    if len(line) == 0:
      continue
    if line[0] == '$':
      vars.append(line)
    elif line[0] == '@':
      line_parts = line.split()
      line = ''
      for part in line_parts:
        line += part
      line = line[:-1]
      if line not in list(labels.keys()):
        labels[line] = len(instructions)
    else:
      instructions.append(line)

  return vars, labels, instructions

def validate_instructions(instructions: list, vars: list, labels: list) -> bool:
  for instruction in instructions:
    instruction_parts = instruction.split(' ')
    opcode = instruction_parts[0]

    if opcode not in OpCodes:
      print(f"[ ERROR : Invalid Instruction ] --> '{instruction}'")
      return False

    if opcode in UnaryOpCodes and len(instruction_parts) > 1:
      print(f"[ ERROR : Invalid Instruction ] --> '{instruction}'")
      return False

    if opcode in BinaryOpCodes and len(instruction_parts) < 2:
      print(f"[ ERROR : Invalid Instruction ] --> '{instruction}'")
      return False

    if opcode in BinaryOpCodes and len(instruction_parts) == 2:
      address = instruction_parts[1]
      if address[0] == '#':

        if address[1] == 'd':
          if address[2:].isdecimal() == False:
            return False

        elif address[1] == 'h':
          for char in address[2:]:
            if char not in '0123456789abcdefABCDEF':
              return False

        elif address[1] == 'b':
          for char in address[2:]:
            if char not in '01':
              return False

      elif instruction_parts[1] not in vars and instruction_parts[1] not in labels:
        print(f"[ ERROR : Invalid Variable/Label ] --> '{instruction}'")
        return False

  return True


def translate(source_file: str, output_file: str):
    preprocessed_data = preprocess(source_file)  # stage: 1

    vars, labels, instructions = vars_and_instructions(preprocessed_data)  # stage: 2

    labels_list = list(labels.keys())

    vars_list = list()
    vars_dict = dict()

    for var in vars:
      var_parts = var.split(' = ')
      var_name = var_parts[0]

      if len(var_parts) < 2:
        var_parts.append('0')

      if var_parts[1][0] == '#':
        if var_parts[1][1] == 'd':
          var_parts[1] = int(var_parts[1][2:], 10)
        elif var_parts[1][1] == 'h':
          var_parts[1] = int(var_parts[1][2:], 16)
        elif var_parts[1][1] == 'b':
          var_parts[1] = int(var_parts[1][2:], 2)
        else:
          var_parts[1] = int(var_parts[1], 10)
      else:
        var_parts[1] = int(var_parts[1], 10)

      vars_dict[var_name] = var_parts[1]

      if var_name not in vars_list:
        vars_list.append(var_name)

    if 'hlt' not in instructions:  # insert 'hlt' instruction, if not present
      instructions.append('hlt')

    if not validate_instructions(instructions, vars_list, labels_list):  # stage: 3
      print("Translation Failed!")
    else:
      lines_with_resolved_addresses = list()
      var_init = len(instructions)

      for instruction in instructions:
        instruction_parts = instruction.split(' ')
        opcode = instruction_parts[0]
        var = instruction_parts[1] if len(instruction_parts) > 1 else '0'

        if var[0] == '#':
          if var[1] == 'd':
            var = int(var[2:], 10)
          elif var[1] == 'h':
            var = int(var[2:], 16)
          elif var[1] == 'b':
            var = int(var[2:], 2)

        elif var in vars_list:
          var = var_init + vars_list.index(var)

        elif var in labels_list:
          var = labels[var]

        var = str(var)

        opcode = opcode_hex_value(opcode)
        address = hex(int(var))[2:].zfill(5)

        lines_with_resolved_addresses.append(f"{opcode}{address}")

      for var in vars_list:
        lines_with_resolved_addresses.append(f"{hex(int(vars_dict[var]))[2:].zfill(7)}")

      for i in range(len(vars_list)):
        lines_with_resolved_addresses[i]

      ram_content = 'v3.0 hex words addressed\n00000:'

      for line in lines_with_resolved_addresses:
        ram_content += (' ' + line)

      with open(output_file, 'w') as RAM:
        RAM.write(ram_content)
        print(f"Translation Successfully Done.\nOutput file: '{output_file}'")


if __name__ == '__main__':
  if len(sys.argv) != 3:
    print("Usage: python translator.py <source_file> <output_file>")
  else:
    source_file = sys.argv[1]
    output_file = sys.argv[2]
    translate(source_file, output_file)
