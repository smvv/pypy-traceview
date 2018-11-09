from ..args import FakeArgs
from ..logparser.pypylog import parse
from ..snippet import resolve_code_snippets
from ..code_dump import resolve_code_dumps
from .html import render


def test_render():
    with open('testcases/simple-add-mod-loop/add.log') as f:
        search_paths = ['testcases/simple-add-mod-loop']
        traces = parse(f)
        resolve_code_snippets(traces, search_paths)
        resolve_code_dumps(FakeArgs(), traces)
        html = render(traces)
        assert html
