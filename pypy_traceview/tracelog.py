from .opcode import Opcode


class TraceLog:
    def __init__(self):
        # Id is set during `pypylog.parse()`.
        self.id = None

        self.raw_opcodes = []
        self.raw_ir = []

        self._files = []
        self._methods = []
        self._opcodes = []

    def _parse_opcodes(self):
        files = set()
        methods = set()
        opcodes = []

        for line in self.raw_opcodes:
            method, line = line.split(';')
            methods.add(method)

            filename, line = line.split(':')
            files.add(filename)

            opcodes.append(Opcode(line, method=method, filename=filename))

        self._files = list(files)
        self._methods = list(methods)
        self._opcodes = opcodes

    @property
    def files(self):
        if not self._files:
            self._parse_opcodes()
        return self._files

    @property
    def methods(self):
        if not self._methods:
            self._parse_opcodes()
        return self._methods

    @property
    def opcodes(self):
        if not self._opcodes:
            self._parse_opcodes()
        return self._opcodes
