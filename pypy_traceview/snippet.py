from pathlib import Path
from .memoization import memoized


@memoized
def find_file(filename, path):
        source_file = Path(path).joinpath(filename)
        if source_file.is_file():
            return source_file


@memoized
def find_snippet(filename, line):
    with open(str(filename)) as f:
        # Find the line in the source file.
        snippet = f.readlines()[line - 1]

        # Strip leading and trailing whitespace.
        return snippet.strip()


def resolve_code_snippets(traces, search_paths):
    for trace in traces:
        last = None

        for opcode in trace.opcodes:
            for path in search_paths:
                filename = find_file(opcode.filename, path)
                if filename:
                    break

            snippet = '# Source file not found'
            if filename:
                snippet = find_snippet(filename, opcode.code_line)

            opcode.snippet = snippet

            # The first instruction after a function call sets the inlined
            # functoin location for the caller.
            if last and last.is_call and filename:
                snippet = find_snippet(filename, opcode.func_line)
                last.method_snippet = snippet

            last = opcode
