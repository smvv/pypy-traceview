from .pypylog import parse


def test_parse_jit_tracing():
    testcase = """
[dc7da3166a65] {jit-tracing
main;add.py:5-7~#19 FOR_ITER
main;add.py:5-7~#22 STORE_FAST
main;add.py:5-8~#25 LOAD_FAST
main;add.py:5-8~#28 LOAD_GLOBAL
main;add.py:5-8~#31 LOAD_FAST
main;add.py:5-8~#34 LOAD_FAST
main;add.py:5-8~#37 LOAD_CONST
main;add.py:5-8~#40 BINARY_MODULO
main;add.py:5-8~#41 CALL_FUNCTION
add;add.py:1-2~#0 LOAD_FAST
add;add.py:1-2~#3 LOAD_FAST
add;add.py:1-2~#6 BINARY_ADD
add;add.py:1-2~#7 RETURN_VALUE
main;add.py:5-8~#44 LOAD_CONST
main;add.py:5-8~#47 BINARY_MODULO
main;add.py:5-8~#48 INPLACE_ADD
main;add.py:5-8~#49 STORE_FAST
main;add.py:5-8~#52 JUMP_ABSOLUTE
main;add.py:5-7~#19 FOR_ITER
[dc7da3979cad] jit-tracing}
    """.strip().split('\n')

    logs = parse(testcase)
    assert len(logs) == 1

    log = logs[0]
    assert len(log.raw_opcodes) == 19
    assert log.raw_opcodes[0] == 'main;add.py:5-7~#19 FOR_ITER'
    assert log.raw_opcodes[18] == 'main;add.py:5-7~#19 FOR_ITER'

    assert log.files == ['add.py']
    assert sorted(log.methods) == ['add', 'main']
    assert len(log.opcodes) == 19


def test_simple_add_mod_loop():
    with open('testcases/simple-add-mod-loop/add.log') as f:
        logs = parse(f)
        assert len(logs) == 2
        assert len(logs[0].raw_opcodes) == 0

        log = logs[1]
        assert len(log.raw_opcodes) == 19
        assert log.files == ['add.py']
        assert sorted(log.methods) == ['add', 'main']
        assert len(log.opcodes) == 19

        assert len(log.raw_ir) == 140
        assert '# Loop' in log.raw_ir[0]
        assert '--end of the loop--' in log.raw_ir[-1]
