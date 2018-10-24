#!/usr/bin/env python
import argparse

description = 'Convert PyPy JIT log file to HTML.'

parser = argparse.ArgumentParser(description=description)

parser.add_argument('file', metavar='FILE', type=str,
                    help='PyPy JIT log filename')

parser.add_argument('--output', '-o', type=str, default='output.html',
                    help='HTML output filename (default: output.html)')


def main():
    args = parser.parse_args()
    print('Opening PyPy log file: {}'.format(args.file))


if __name__ == '__main__':
    main()
