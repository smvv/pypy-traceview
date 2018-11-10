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

    output = p.stdout.decode('utf-8')

    # Remove leading whitespace from lines
    output = output.replace('\n  ', '\n')
    output = output.replace('\t', '  ')

    lines = output.splitlines()

    # Strip objdump header from output
    lines = lines[7:]

    return lines


def determine_maximum_offset_text_width(lines):
    # Find the last line with a colon in it.
    for i in range(1, len(lines) + 1):
        last_line = lines[-i]
        if ':' in last_line:
            break

    assert ':' in last_line, last_line

    # Split the offset from the content and compute its maximum string length.
    offset, _ = last_line.split(':', 1)
    offset = int(offset.strip(), 16)
    return len(str(offset))


def convert_offsets_to_digits(lines):
    max_width = determine_maximum_offset_text_width(lines)

    for i, line in enumerate(lines):
        parts = line.split(':', 1)

        if len(parts) < 2:
            continue

        offset, content = parts
        offset = int(offset.strip(), 16)

        lines[i] = ('{:' + str(max_width) + 'd}: {}').format(offset, content)

    return lines


def resolve_code_dump(args, lines):
    objdump = find_objdump()

    dump = CodeDump(lines)

    machine = objdump_machine_option[dump.backend_name]
    machine_code = bytes.fromhex(dump.code)

    with tempfile.NamedTemporaryFile() as f:
        f.write(machine_code)
        f.flush()

        flags = [
            '-b', 'binary',
            '-m', machine,
            '--no-show-raw-insn',
            '-D',
        ]

        if args.mnemonics == 'intel':
            flags.append('--disassembler-options=intel-mnemonics')

        code = disassemble_machine_code(objdump, flags, f.name)

        code = convert_offsets_to_digits(code)

        dump.code = code

    return dump


def resolve_code_dumps(args, traces):
    for trace in traces:
        # Only display the first code dump. The others are not relevant.
        trace.code_dumps = [
            resolve_code_dump(args, dump)
            for dump in trace.code_dumps[:1]
        ]
