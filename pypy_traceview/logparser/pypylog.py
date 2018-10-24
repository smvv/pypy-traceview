"""
This file implements a state machine for parsing PYPYLOG output files.
"""
from ..tracelog import TraceLog


# Enable this flag to display verbose trace messages of the state machine.
trace_parser = False


def trace_step(fn):
    def enable_log(line, state):
        print(fn.__name__[6:] + ':', line)
        return fn(line, state)

    if trace_parser:
        return enable_log

    return fn


def is_jit_tracing_start(line):
    return line.endswith('{jit-tracing')


def is_jit_tracing_end(line):
    return line.endswith('jit-tracing}')


def is_jit_trace_done_start(line):
    return line.endswith('{jit-trace-done')


def is_jit_trace_done_end(line):
    return line.endswith('jit-trace-done}')


def is_jit_starting(line):
    return line.startswith('JIT starting (')


@trace_step
def parse_jit_trace_done_start(line, state):
    if is_jit_tracing_end(line):
        return parse_jit_tracing_end

    return parse_jit_trace_done_start


@trace_step
def parse_jit_tracing_end(line, state):
    assert state['log']
    state['logs'].append(state['log'])
    state['log'] = None
    return parse_end(line, state)


@trace_step
def parse_jit_starting(line, state):
    if is_jit_tracing_end(line):
        return parse_jit_tracing_end(line, state)

    return parse_jit_starting


@trace_step
def parse_jit_tracing_start(line, state):
    if is_jit_tracing_end(line):
        return parse_jit_tracing_end(line, state)

    if is_jit_trace_done_start(line):
        return parse_jit_trace_done_start

    # Start a new trace log
    if not state['log']:
        state['log'] = TraceLog()

    if is_jit_starting(line):
        return parse_jit_starting

    # Collect the successive lines (= opcodes).
    assert line[0] != '['
    state['log'].raw_opcodes.append(line)

    return parse_jit_tracing_start


@trace_step
def parse_start(line, state):
    if is_jit_tracing_start(line):
        return parse_jit_tracing_start

    return parse_start


@trace_step
def parse_end(line, state):
    return parse_start


def parse(logfile):
    state = {'log': None, 'logs': []}

    fn = parse_start

    for line in logfile:
        # Strip newline char from line
        fn = fn(line.rstrip(), state)

    assert fn == parse_start

    return state['logs']
