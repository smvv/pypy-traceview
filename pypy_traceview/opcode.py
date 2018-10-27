class Opcode:
    def __init__(self, opcode, method=None, filename=None):
        parts = opcode.split('~')
        assert len(parts) == 2, opcode

        func_line, code_line = parts[0].split('-')
        self.func_line = int(func_line)
        self.code_line = int(code_line)

        id, name = parts[1].split(' ')
        assert id[0] == '#', opcode
        self.id = int(id[1:])
        self.name = name

        self.method = method
        self.filename = filename

        self.snippet = None

    def __repr__(self):
        return '<Opcode "{}">'.format(self.name)


def count_opcodes(opcodes):
    count = 0

    for opcode in opcodes:
        if isinstance(opcode, list):
            count += count_opcodes(opcode)
        else:
            count += 1

    return count


def group_opcodes(opcodes):
    if not opcodes:
        return []

    groups = []

    last = None
    group = []

    for opcode in opcodes:
        if isinstance(opcode, list):
            if group:
                groups.append(group)
            groups.append(group_opcodes(opcode))
            group = []
            last = None
        elif not last or opcode.code_line == last.code_line:
            group.append(opcode)
            last = opcode
        else:
            if group:
                groups.append(group)
            group = [opcode]
            last = opcode

    if group:
        groups.append(group)

    assert count_opcodes(groups) == count_opcodes(opcodes)

    return groups


def dump_indentend_opcodes(stack, indent=0):
    for children in stack:
        if isinstance(children, list):
            dump_indentend_opcodes(children, indent=indent + 1)
        else:
            print('  ' * indent + str(children))


def indent_opcodes(opcodes):
    level = 0
    stack = [[]]
    last = None

    for opcode in opcodes:
        # Ignore second FOR_ITER opcode that marks end of for loop.
        if opcode.name == 'FOR_ITER' and last and last.name == 'JUMP_ABSOLUTE':
            last = opcode
            continue

        stack[level].append(opcode)

        if opcode.name == 'FOR_ITER' or opcode.name == 'CALL_FUNCTION':
            level += 1
            if len(stack) < level:
                stack[level] = []
            else:
                stack.append([])

            last = opcode
            continue

        if opcode.name == 'JUMP_ABSOLUTE' or opcode.name == 'RETURN_VALUE':
            children = stack[level]

            if len(stack) == level + 1:
                stack.pop()
            else:
                stack[level] = []

            level -= 1
            assert level >= 0
            stack[level].append(children)

            last = opcode
            continue

        last = opcode

    assert level == 0

    return stack[0]
