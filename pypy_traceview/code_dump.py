import os
import tempfile
import subprocess

from .memoization import memoized


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


class ObjdumpNotFound(Exception):
    pass


@memoized
def find_objdump():
    # This function comes from PyPy's `rpython/jit/backend/tool/viewcode.py`,
    # but the order for checking the executables is different. It will try to
    # find `gobjdump` first since `objdump` can also refer to LLVM's objdump.
    exe = ('gobjdump', 'objdump', 'objdump.exe')
    path = os.environ['PATH'].split(os.pathsep)
    for e in exe:
        for p in path:
            path_to = os.path.join(p, e)
            if not os.path.exists(path_to):
                continue
            return e
    raise ObjdumpNotFound('(g)objdump was not found in PATH')


objdump_machine_option = {
    'x86': 'i386',
    'x86-without-sse2': 'i386',
    'x86_32': 'i386',
    'x86_64': 'i386:x86-64',
    'x86-64': 'i386:x86-64',
    'i386': 'i386',
    'arm': 'arm',
    'arm_32': 'arm',
    'ppc': 'powerpc:common64',
    'ppc-64': 'powerpc:common64',
    's390x': 's390:64-bit',
}


def disassemble_machine_code(objdump, flags, filename):
    cmd = [objdump, *flags, filename]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if p.stderr:
        print('command:', ' '.join(cmd))
        print(p.stderr.decode('utf-8'))

    assert p.returncode == 0
    assert not p.stderr

    lines = p.stdout.decode('utf-8').splitlines()

    # Strip objdump header from output
    return lines[7:]


def resolve_code_dump(lines):
    objdump = find_objdump()

    dump = CodeDump(lines)

    machine = objdump_machine_option[dump.backend_name]

    with tempfile.NamedTemporaryFile() as f:
        f.write(bytes.fromhex(dump.code))
        f.flush()

        flags = [
            '-b', 'binary',
            '-m', machine,
            '--disassembler-options=intel-mnemonics',
            '-D',
        ]

        dump.code = disassemble_machine_code(objdump, flags, f.name)

    return dump


def resolve_code_dumps(traces):
    for trace in traces:
        trace.code_dumps = list(map(resolve_code_dump, trace.code_dumps))
