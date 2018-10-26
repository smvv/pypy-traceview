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
