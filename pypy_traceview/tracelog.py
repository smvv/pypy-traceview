class TraceLog:
    def __init__(self):
        self.raw_opcodes = []

    @property
    def files(self):
        return list(set([
            opcode.split(':')[0].split(';')[1]
            for opcode in self.raw_opcodes
        ]))

    @property
    def methods(self):
        return list(set([
            opcode.split(';')[0]
            for opcode in self.raw_opcodes
        ]))
