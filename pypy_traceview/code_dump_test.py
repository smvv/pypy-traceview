from .code_dump import resolve_code_dump

basic_code_dump = """
BACKEND x86_64
SYS_EXECUTABLE /path/to/bin/python
CODE_DUMP @10c4bd023 +0  12020000
""".strip().split('\n')


def test_basic_code_dump():
    dump = resolve_code_dump(basic_code_dump)
    assert dump.backend_name == 'x86_64'
    assert dump.executable == '/path/to/bin/python'

    # Check if the code disassembles to 'adc (%rdx),%al'
    assert 'adc ' in dump.code[0]
    assert '%rdx' in dump.code[0]
    assert '%al' in dump.code[0]

    assert dump.address == 0x10c4bd023
    assert dump.offset == 0
