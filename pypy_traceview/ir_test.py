from .logparser.pypylog import parse
from .ir import group_ir


def test_simple_add_mod_loop():
    with open('testcases/simple-add-mod-loop/add.log') as f:
        traces = parse(f)
        _, trace = traces

        assert len(trace.opcodes) == 19
        assert len(trace.raw_ir) == 140
        assert '# Loop' in trace.raw_ir[0]
        assert '--end of the loop--' in trace.raw_ir[-1]

        groups = group_ir(trace.raw_ir)
        assert len(groups) == 60

        merge_points = [
            group[0]
            for group in groups
            if group[0].startswith('debug_merge_point')
        ]
        print('\n'.join(merge_points))
        assert len(merge_points) == 38
