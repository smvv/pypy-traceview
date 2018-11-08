#!/usr/bin/env python
import argparse
import io
import cProfile
import pstats

from pathlib import Path

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


def prefilter_trace(trace):
    """
    This filter is applied before resolving code snippets.
    """
    return trace.opcodes


def postfilter_trace(trace):
    """
    This filter is applied after resolving code snippets.
    """
    return trace.raw_ir


def filter_traces(fn, traces):
    traces_before_filtering = len(traces)
    traces = list(filter(fn, traces))
    filtered = traces_before_filtering - len(traces)
    return traces, filtered


def main():
    args = parser.parse_args()

    if args.profile:
        pr = cProfile.Profile()
        pr.enable()

    print('Opening PyPy log file: {}'.format(args.file))

    with open(args.file) as f:
        search_paths = [Path(args.file).parent]

        print('Parsing PyPy log file')
        traces = parse(f)

        traces, filtered = filter_traces(prefilter_trace, traces)
        if filtered:
            print('Filtered {} traces'.format(filtered))

        print('Resolving code snippets')
        resolve_code_snippets(traces, search_paths)

        traces, filtered = filter_traces(postfilter_trace, traces)
        if filtered:
            print('Filtered {} traces'.format(filtered))

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
