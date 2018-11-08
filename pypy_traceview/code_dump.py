class CodeDump:
    def __init__(self, lines):
        backend_name, executable, code, address, offset = self._parse(lines)
        self.backend_name = backend_name
        self.executable = executable
        self.code = code
        self.address = address
        self.offset = offset

    def _parse(self, lines):
        backend_name = None
        executable = None
        code = None
        address = None
        offset = None

        for line in lines:
            if line.startswith('BACKEND '):
                assert not backend_name
                backend_name = line[8:]

            elif line.startswith('SYS_EXECUTABLE '):
                assert not executable
                executable = line[15:]

            elif line.startswith('CODE_DUMP '):
                assert not code
                assert not address
                assert not offset
                line = line[10:]

                address, offset, code = line.split()

                assert address[0] == '@'
                address = int(address[1:], 16)

                assert offset[0] == '+'
                offset = int(offset)
                assert offset == 0

        return backend_name, executable, code, address, offset
