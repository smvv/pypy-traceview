from .code_dump import CodeDump

basic_code_dump = """
BACKEND x86_64
SYS_EXECUTABLE /path/to/bin/python
CODE_DUMP @10c4bd023 +0  12020000
""".strip().split('\n')


def test_basic_code_dump():
    dump = CodeDump(basic_code_dump)
    assert dump.backend_name == 'x86_64'
    assert dump.executable == '/path/to/bin/python'
    assert dump.code == '12020000'
    assert dump.address == 0x10c4bd023
    assert dump.offset == 0
