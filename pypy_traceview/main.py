#!/usr/bin/env python
import argparse

from pypy_traceview.logparser.pypylog import parse
from pypy_traceview.snippet import resolve_code_snippets
from pypy_traceview.renderer.html import render

description = 'Convert PyPy JIT log file to HTML.'

parser = argparse.ArgumentParser(description=description)

parser.add_argument('file', metavar='FILE', type=str,
                    help='PyPy JIT log filename')

parser.add_argument('--output', '-o', type=str, default='output.html',
                    help='HTML output filename (default: output.html)')


def main():
    args = parser.parse_args()
    print('Opening PyPy log file: {}'.format(args.file))

    with open(args.file) as f:
        # TODO
        search_paths = ['testcases/simple-add-mod-loop']
        traces = parse(f)
        resolve_code_snippets(traces, search_paths)
        html = render(traces)

    with open(args.output, 'w') as f:
        f.write(html)


if __name__ == '__main__':
    main()
