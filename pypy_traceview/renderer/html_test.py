from ..logparser.pypylog import parse
from ..opcode import Opcode
from ..snippet import resolve_code_snippets
from .html import render, group_opcodes


def test_group_opcodes():
    opcodes = [
        Opcode("5-7~#19 FOR_ITER"),
        Opcode("5-7~#22 STORE_FAST"),
        Opcode("5-8~#25 LOAD_FAST"),
        Opcode("5-8~#28 LOAD_GLOBAL"),
        Opcode("5-8~#31 LOAD_FAST"),
        Opcode("5-8~#34 LOAD_FAST"),
        Opcode("5-8~#37 LOAD_CONST"),
        Opcode("5-8~#40 BINARY_MODULO"),
        Opcode("5-8~#41 CALL_FUNCTION"),
        Opcode("1-2~#0 LOAD_FAST"),
        Opcode("1-2~#3 LOAD_FAST"),
        Opcode("1-2~#6 BINARY_ADD"),
        Opcode("1-2~#7 RETURN_VALUE"),
        Opcode("5-8~#44 LOAD_CONST"),
        Opcode("5-8~#47 BINARY_MODULO"),
        Opcode("5-8~#48 INPLACE_ADD"),
        Opcode("5-8~#49 STORE_FAST"),
        Opcode("5-8~#52 JUMP_ABSOLUTE"),
        Opcode("5-7~#19 FOR_ITER"),
    ]

    groups = group_opcodes(opcodes)

    assert len(groups) == 5


def test_render():
    with open('testcases/simple-add-mod-loop/add.log') as f:
        search_paths = ['testcases/simple-add-mod-loop']
        traces = parse(f)
        resolve_code_snippets(traces, search_paths)
        html = render(traces)
        assert html
