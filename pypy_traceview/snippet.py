from pathlib import Path


# TODO: add memoization here
def find_file(filename, search_paths):
    for path in search_paths:
        source_file = Path(path).joinpath(filename)
        if source_file.is_file():
            return source_file


# TODO: add memoization here
def find_snippet(filename, line):
    with open(str(filename)) as f:
        # Find the line in the source file.
        snippet = f.readlines()[line - 1]

        # Strip leading and trailing whitespace.
        return snippet.strip()


def resolve_code_snippets(traces, search_paths):
    for trace in traces:
        for opcode in trace.opcodes:
            filename = find_file(opcode.filename, search_paths)

            snippet = '# Source file not found'
            if filename:
                snippet = find_snippet(filename, opcode.code_line)

            opcode.snippet = snippet
