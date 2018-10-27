from .opcode import Opcode, group_opcodes, indent_opcodes, \
    dump_indentend_opcodes


def test_opcode():
    opcode = Opcode('5-7~#19 FOR_ITER')
    assert opcode.func_line == 5
    assert opcode.code_line == 7
    assert opcode.id == 19
    assert opcode.name == 'FOR_ITER'
    assert not opcode.filename
    assert not opcode.method
    assert not opcode.snippet


def test_opcode_with_filename_and_method():
    filename = 'add.py'
    method = 'main'
    opcode = Opcode('5-7~#19 FOR_ITER', method=method, filename=filename)
    assert opcode.func_line == 5
    assert opcode.code_line == 7
    assert opcode.id == 19
    assert opcode.name == 'FOR_ITER'
    assert opcode.filename == filename
    assert opcode.method == method
    assert not opcode.snippet


basic_opcodes = [
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


def test_group_basic_opcodes():
    groups = group_opcodes(basic_opcodes)
    assert len(groups) == 5


def test_indent_basic_opcodes():
    # This test expects the following indentation of opcodes:
    #
    # 0  <Opcode "FOR_ITER">
    # 1  0  <Opcode "STORE_FAST">
    #    1  <Opcode "LOAD_FAST">
    #    2  <Opcode "LOAD_GLOBAL">
    #    3  <Opcode "LOAD_FAST">
    #    4  <Opcode "LOAD_FAST">
    #    5  <Opcode "LOAD_CONST">
    #    6  <Opcode "BINARY_MODULO">
    #    7  <Opcode "CALL_FUNCTION">
    #    8  0 <Opcode "LOAD_FAST">
    #       1 <Opcode "LOAD_FAST">
    #       2 <Opcode "BINARY_ADD">
    #       3 <Opcode "RETURN_VALUE">
    #    9  <Opcode "LOAD_CONST">
    #    10 <Opcode "BINARY_MODULO">
    #    11 <Opcode "INPLACE_ADD">
    #    12 <Opcode "STORE_FAST">
    #    13 <Opcode "JUMP_ABSOLUTE">

    indented = indent_opcodes(basic_opcodes)
    dump_indentend_opcodes(indented)

    assert len(indented) == 2
    assert indented[0].name == 'FOR_ITER'
    assert isinstance(indented[1], list)
    assert len(indented[1]) == 14
    assert indented[1][-1].name == 'JUMP_ABSOLUTE'

    assert isinstance(indented[1][8], list)
    assert len(indented[1][8]) == 4
    assert indented[1][8][-1].name == 'RETURN_VALUE'
