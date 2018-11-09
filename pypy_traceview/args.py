import argparse


class FakeArgs:
    def __init__(self):
        self.mnemonics = 'att'


description = 'Convert PyPy JIT log file to HTML.'

parser = argparse.ArgumentParser(description=description)

parser.add_argument('file', metavar='FILE', type=str,
                    help='PyPy JIT log filename')

parser.add_argument('--output', '-o', type=str, default='output.html',
                    help='HTML output filename (default: output.html)')

parser.add_argument('--profile', action='store_true',
                    help='Dump CPU profiler info')

parser.add_argument('--mnemonics', type=str, default='att',
                    help='Disassemble using "intel" or "att" (default) syntax')
