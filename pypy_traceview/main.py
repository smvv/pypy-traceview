#!/usr/bin/env python
import argparse
import io
import cProfile
import pstats

from pypy_traceview.logparser.pypylog import parse
from pypy_traceview.snippet import resolve_code_snippets
from pypy_traceview.renderer.html import render

description = 'Convert PyPy JIT log file to HTML.'

parser = argparse.ArgumentParser(description=description)

parser.add_argument('file', metavar='FILE', type=str,
                    help='PyPy JIT log filename')

parser.add_argument('--output', '-o', type=str, default='output.html',
                    help='HTML output filename (default: output.html)')

parser.add_argument('--profile', action='store_true',
                    help='Dump CPU profiler info')


def main():
    args = parser.parse_args()

    if args.profile:
        pr = cProfile.Profile()
        pr.enable()

    print('Opening PyPy log file: {}'.format(args.file))

    with open(args.file) as f:
        # TODO
        search_paths = ['testcases/simple-add-mod-loop']

        print('Parsing PyPy log file')
        traces = parse(f)

        print('Resolving code snippets')
        resolve_code_snippets(traces, search_paths)

        print('Rendering HTML output')
        html = render(traces)

    with open(args.output, 'w') as f:
        print('Writing to HTML output file: {}'.format(args.output))
        f.write(html)

    if args.profile:
        pr.disable()
        stream = io.StringIO()
        ps = pstats.Stats(pr, stream=stream).strip_dirs().sort_stats('cumtime')
        ps.print_stats(20)
        print(stream.getvalue())


if __name__ == '__main__':
    main()
