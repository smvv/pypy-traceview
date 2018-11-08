class Opcode:
    def __init__(self, opcode, method=None, filename=None):
        parts = opcode.split('~')
        if len(parts) != 2:
            raise ValueError(opcode)

        func_line, code_line = parts[0].split('-')
        self.func_line = int(func_line)
        self.code_line = int(code_line)

        id, name = parts[1].split(' ', 1)
        if id[0] != '#':
            raise ValueError(opcode)

        self.id = int(id[1:])
        self.name = name

        self.method = method
        self.filename = filename

        self.snippet = None
        self.method_snippet = None

        self._init_opcode_flags()

    def _init_opcode_flags(self):
        self.is_call = self.name in ['CALL_FUNCTION', 'CALL_METHOD']

    def __repr__(self):
        return '<Opcode "{}-{}~#{} {}">'.format(self.func_line, self.code_line,
                                                self.id, self.name)

    def __eq__(self, other):
        return self.id == other.id \
                and self.func_line == other.func_line \
                and self.code_line == other.code_line \
                and self.name == other.name \
                and self.method == other.method \
                and self.filename == other.filename \
                and self.snippet == other.snippet \
                and self.method_snippet == other.method_snippet


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


def dump_opcodes(opcodes):
    for opcode in opcodes:
        print(opcode)


def _push(stack, level):
    level += 1
    if len(stack) < level:
        stack[level] = []
    else:
        stack.append([])
    return level


def _pop(stack, level):
    children = stack[level]

    if len(stack) == level + 1:
        stack.pop()
    else:
        stack[level] = []

    level -= 1
    assert level >= 0
    stack[level].append(children)
    return level


def indent_opcodes(opcodes):
    level = 0
    stack = [[]]
    last = None

    for opcode in opcodes:
        # Ignore second FOR_ITER opcode that marks end of for loop.
        if opcode.name == 'FOR_ITER' and level > 0 \
                and opcode == stack[level - 1][0]:
            level = _pop(stack, level)
            last = opcode
            continue

        # Move opcode STORE_FAST after a FOR_ITER into the FOR_ITER scope. This
        # avoids having the same "for i in ..." code snippet inside the loop
        # block.
        if opcode.name == 'STORE_FAST' and last and last.name == 'FOR_ITER':
            assert level > 0
            stack[level - 1].append(opcode)
            last = opcode
            continue

        stack[level].append(opcode)

        if opcode.name == 'FOR_ITER' or opcode.is_call:
            level = _push(stack, level)
            last = opcode
            continue

        if opcode.name == 'RETURN_VALUE':
            level = _pop(stack, level)
            last = opcode
            continue

        last = opcode

    assert level == 0

    return stack[0]
