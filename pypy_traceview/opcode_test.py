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
    # 1  <Opcode "STORE_FAST">
    # 1  0  <Opcode "LOAD_FAST">
    #    1  <Opcode "LOAD_GLOBAL">
    #    2  <Opcode "LOAD_FAST">
    #    3  <Opcode "LOAD_FAST">
    #    4  <Opcode "LOAD_CONST">
    #    5  <Opcode "BINARY_MODULO">
    #    6  <Opcode "CALL_FUNCTION">
    #    7  0 <Opcode "LOAD_FAST">
    #       1 <Opcode "LOAD_FAST">
    #       2 <Opcode "BINARY_ADD">
    #       3 <Opcode "RETURN_VALUE">
    #    8  <Opcode "LOAD_CONST">
    #    9  <Opcode "BINARY_MODULO">
    #    10 <Opcode "INPLACE_ADD">
    #    11 <Opcode "STORE_FAST">
    #    12 <Opcode "JUMP_ABSOLUTE">

    indented = indent_opcodes(basic_opcodes)
    dump_indentend_opcodes(indented)

    assert len(indented) == 3

    assert indented[0].name == 'FOR_ITER'
    assert indented[1].name == 'STORE_FAST'

    assert isinstance(indented[2], list)
    loop_block = indented[2]

    assert len(loop_block) == 13
    assert loop_block[-1].name == 'JUMP_ABSOLUTE'

    function_body = loop_block[7]
    assert isinstance(function_body, list)
    assert len(function_body) == 4
    assert function_body[-1].name == 'RETURN_VALUE'


def test_group_indented_basic_opcodes():
    # This test expects the following groups of indented opcodes:
    #
    # 0 [ <Opcode "FOR_ITER">
    #     <Opcode "STORE_FAST"> ]
    # 1 0 [ <Opcode "LOAD_FAST">
    #       <Opcode "LOAD_GLOBAL">
    #       <Opcode "LOAD_FAST">
    #       <Opcode "LOAD_FAST">
    #       <Opcode "LOAD_CONST">
    #       <Opcode "BINARY_MODULO">
    #       <Opcode "CALL_FUNCTION"> ]
    #   1 0 [ <Opcode "LOAD_FAST">
    #         <Opcode "LOAD_FAST">
    #         <Opcode "BINARY_ADD">
    #         <Opcode "RETURN_VALUE"> ]
    #   2 [ <Opcode "LOAD_CONST">
    #       <Opcode "BINARY_MODULO">
    #       <Opcode "INPLACE_ADD">
    #       <Opcode "STORE_FAST">
    #       <Opcode "JUMP_ABSOLUTE"> ]

    indented = indent_opcodes(basic_opcodes)
    groups = group_opcodes(indented)
    assert len(groups) == 2

    loop_header = groups[0]
    assert len(loop_header) == 2

    loop_body = groups[1]
    assert len(loop_body) == 3

    function_body = loop_body[1]
    assert len(function_body) == 1
    assert function_body[0][0].name == 'LOAD_FAST'
    assert function_body[0][-1].name == 'RETURN_VALUE'

    assert loop_body[2][0].name == 'LOAD_CONST'
    assert loop_body[2][-1].name == 'JUMP_ABSOLUTE'
