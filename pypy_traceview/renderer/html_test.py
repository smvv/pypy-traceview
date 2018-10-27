from ..logparser.pypylog import parse
from ..snippet import resolve_code_snippets
from .html import render


def test_render():
    with open('testcases/simple-add-mod-loop/add.log') as f:
        search_paths = ['testcases/simple-add-mod-loop']
        traces = parse(f)
        resolve_code_snippets(traces, search_paths)
        html = render(traces)
        assert html
