from .opcode import Opcode


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
