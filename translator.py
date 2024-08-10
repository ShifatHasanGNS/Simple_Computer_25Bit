# Author: Md. Shifat Hasan (2107067)

import sys

OpCodes = ['noop', 'set', 'clr', 'not', 'neg', 'and', 'or', 'xor', 'add', 'sub', 'mul', 'div', 'shl',
           'shr', 'cmp', 'jmp', 'jmpz', 'jmpl', 'jmpg', 'ina', 'inx', 'outa', 'outx', 'showf', 'show', 'hlt']

UnaryOpCodes = ['noop', 'not', 'neg', 'shl', 'shr', 'showf', 'hlt']

BinaryOpCodes = ['set', 'clr', 'and', 'or', 'xor', 'add', 'sub', 'mul', 'div',
                 'cmp', 'jmp', 'jmpz', 'jmpl', 'jmpg', 'ina', 'inx', 'outa', 'outx', 'show']


def opcode_hex_value(opcode: str):
    id = OpCodes.index(opcode)
    id = hex(id)[2:].zfill(2)
    return id


def content_from_lines(lines: list) -> str:
    return '\n'.join(lines)


def preprocess(source_file: str) -> str:
    with open(source_file, 'r') as file:
        lines = file.readlines()

    # Process the lines in a single loop
    processed_lines = []
    for line in lines:
        line = line.lower().replace(':', ':\n').strip()  # Lowercase, replace, and strip in one step
        line = line.split('!')[0].strip()  # Remove comments and trailing whitespace
        if line:  # Only add non-empty lines
            processed_lines.append(line)

    return content_from_lines(processed_lines)


def vars_and_instructions(content: str) -> tuple:
    lines = content.splitlines()
    vars = [line for line in lines if line.startswith('$')]
    labels = {}
    instructions = []

    for line in lines:
        if not line:
            continue
        if line.startswith('@'):
            label = ''.join(line.split())[:-1]
            if label not in labels:
                labels[label] = len(instructions)
        elif not line.startswith('$'):
            instructions.append(line)

    return vars, labels, instructions


def validate_instructions(instructions: list, vars: list, labels: list) -> bool:
    hex_chars = set('0123456789abcdefABCDEF')
    binary_chars = set('01')

    def is_valid_address(address: str, opcode: str) -> bool:
        if opcode in ['set', 'clr']:
            valid_flag_numbers = {
                '0', '1', '2', '3',
                '#0', '#1', '#2', '#3',
                '#d0', '#d1', '#d2', '#d3',
                '#h0', '#h1', '#h2', '#h3'
            }
            return address in valid_flag_numbers

        if address in vars or address in labels:
            return True

        if address[0] == '#':
            if address[1] == 'd':
                return address[2:].isdigit()
            elif address[1] == 'h':
                return all(c in hex_chars for c in address[2:])
            elif address[1] == 'b':
                return all(c in binary_chars for c in address[2:])
            else:
                return address[1:].isdigit()

        return address.isdigit()

    for instruction in instructions:
        instruction_parts = instruction.split(' ')
        if not instruction_parts:
            print(f"[ ERROR : Invalid Instruction ] --> '{instruction}'")
            return False

        opcode = instruction_parts[0]
        if opcode not in OpCodes:
            print(f"[ ERROR : Invalid Instruction ] --> '{instruction}'")
            return False

        if (opcode in UnaryOpCodes and len(instruction_parts) > 1) or \
           (opcode in BinaryOpCodes and len(instruction_parts) < 2):
            print(f"[ ERROR : Invalid Instruction ] --> '{instruction}'")
            return False

        address = instruction_parts[1] if len(instruction_parts) > 1 else '0'

        if not is_valid_address(address, opcode):
            print(f"[ ERROR : Invalid Instruction ] --> '{instruction}'")
            return False

    return True


def translate(source_file: str, output_file: str):
    preprocessed_data = preprocess(source_file)  # Stage: 1

    vars, labels, instructions = vars_and_instructions(preprocessed_data)  # Stage: 2

    labels_list = list(labels.keys())
    vars_dict = {}
    vars_list = []

    # Processing variables
    for var in vars:
        var_name, var_value = (var.split(' = ') + ['0'])[:2]

        if var_value.startswith('#'):
            base = {'d': 10, 'h': 16, 'b': 2}.get(var_value[1], 10)
            var_value = int(var_value[2:], base)
        else:
            var_value = int(var_value, 10)

        vars_dict[var_name] = var_value
        if var_name not in vars_list:
            vars_list.append(var_name)

    # Ensure 'hlt' instruction is present
    if not instructions or instructions[-1] != 'hlt':
        instructions.append('hlt')

    if not validate_instructions(instructions, vars_list, labels_list):  # Stage: 3
        print("Translation Failed!")
        return

    lines_with_resolved_addresses = []
    var_init = len(instructions)

    # Resolving addresses
    for instruction in instructions:
        parts = instruction.split()
        opcode = parts[0]
        var = parts[1] if len(parts) > 1 else '0'

        if var.startswith('#'):
            base = {'d': 10, 'h': 16, 'b': 2}.get(var[1], 10)
            var = int(var[2:], base)

        if var in vars_list:
            var = var_init + vars_list.index(var)
        elif var in labels_list:
            var = labels[var]

        address = hex(int(var))[2:].zfill(5)
        opcode = opcode_hex_value(opcode)
        lines_with_resolved_addresses.append(f"{opcode}{address}")

    # Adding variable values to the end
    for var in vars_list:
        lines_with_resolved_addresses.append(f"{hex(vars_dict[var])[2:].zfill(7)}")

    # Building RAM content
    ram_content = 'v3.0 hex words addressed\n00000: ' + ' '.join(lines_with_resolved_addresses)

    with open(output_file, 'w') as RAM:
        RAM.write(ram_content)

    print(f"Translation Successfully Done.\nOutput file: '{output_file}'")


if __name__ == '__main__':
    print()
    if len(sys.argv) != 3:
        print("Usage: python translator.py <source_file> <output_file>")
    else:
        source_file = sys.argv[1]
        output_file = sys.argv[2]
        translate(source_file, output_file)
    print()
