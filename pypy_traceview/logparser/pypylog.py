"""
This file implements a state machine for parsing PYPYLOG output files.
"""
import os

from ..tracelog import TraceLog


# Enable this flag to display verbose trace messages of the state machine.
trace_parser = os.getenv('TRACE_PARSER')


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


def is_jit_log_opt_loop_start(line):
    return line.endswith('{jit-log-opt-loop')


def is_jit_log_opt_loop_end(line):
    return line.endswith('jit-log-opt-loop}')


def is_jit_optimize_start(line):
    return line.endswith('{jit-optimize')


def is_jit_optimize_end(line):
    return line.endswith('jit-optimize}')


def is_jit_backend_start(line):
    return line.endswith('{jit-backend')


def is_jit_backend_end(line):
    return line.endswith('jit-backend}')


def is_jit_backend_dump_start(line):
    return line.endswith('{jit-backend-dump')


def is_jit_backend_dump_end(line):
    return line.endswith('jit-backend-dump}')


def is_jit_backend_addr_start(line):
    return line.endswith('{jit-backend-addr')


def is_jit_backend_addr_end(line):
    return line.endswith('jit-backend-addr}')


def is_jit_log_short_preamble_start(line):
    return line.endswith('{jit-log-short-preamble')


def is_jit_log_short_preamble_end(line):
    return line.endswith('jit-log-short-preamble}')


def is_jit_log_rewritten_loop_start(line):
    return line.endswith('{jit-log-rewritten-loop')


def is_jit_log_rewritten_loop_end(line):
    return line.endswith('jit-log-rewritten-loop}')


def is_jit_log_opt_bridge_start(line):
    return line.endswith('{jit-log-opt-bridge')


def is_jit_log_opt_bridge_end(line):
    return line.endswith('jit-log-opt-bridge}')


def is_jit_mem_collect_start(line):
    return line.endswith('{jit-mem-collect')


def is_jit_mem_collect_end(line):
    return line.endswith('jit-mem-collect}')


def is_jit_mem_looptoken_alloc_start(line):
    return line.endswith('{jit-mem-looptoken-alloc')


def is_jit_mem_looptoken_alloc_end(line):
    return line.endswith('jit-mem-looptoken-alloc}')


def is_jit_trace_done_start(line):
    return line.endswith('{jit-trace-done')


def is_jit_trace_done_end(line):
    return line.endswith('jit-trace-done}')


def is_jit_summary_start(line):
    return line.endswith('{jit-summary')


def is_jit_summary_end(line):
    return line.endswith('jit-summary}')


def is_jit_backend_counts_start(line):
    return line.endswith('{jit-backend-counts')


def is_jit_backend_counts_end(line):
    return line.endswith('jit-backend-counts}')


def is_jit_starting(line):
    return line.startswith('JIT starting (')


@trace_step
def parse_jit_log_opt_loop(line, state):
    if is_jit_tracing_end(line):
        return parse_jit_tracing_end

    if is_jit_log_opt_loop_end(line):
        return parse_jit_tracing_end

    # Collect the successive lines (= PyPy IR).
    state['log'].raw_ir.append(line)

    return parse_jit_log_opt_loop


@trace_step
def parse_jit_trace_done_start(line, state):
    if is_jit_tracing_end(line):
        return parse_jit_tracing_end

    if is_jit_log_opt_loop_start(line):
        return parse_jit_log_opt_loop

    if is_jit_trace_done_end(line):
        return parse_jit_tracing_start

    return parse_jit_trace_done_start


@trace_step
def parse_jit_optimize(line, state):
    if is_jit_optimize_end(line):
        return parse_jit_tracing_start

    return parse_jit_optimize


@trace_step
def parse_jit_log_short_preamble(line, state):
    if is_jit_log_short_preamble_end(line):
        return parse_jit_tracing_start

    return parse_jit_log_short_preamble


@trace_step
def parse_jit_log_rewritten_loop(line, state):
    if is_jit_log_rewritten_loop_end(line):
        return parse_jit_tracing_start

    return parse_jit_log_rewritten_loop


@trace_step
def parse_jit_log_opt_bridge(line, start):
    if is_jit_log_opt_bridge_end(line):
        return parse_jit_tracing_start

    return parse_jit_log_opt_bridge


@trace_step
def parse_jit_mem_collect(line, start):
    if is_jit_mem_collect_end(line):
        return parse_jit_tracing_start

    return parse_jit_mem_collect


@trace_step
def parse_jit_mem_looptoken_alloc(line, start):
    if is_jit_mem_looptoken_alloc_end(line):
        return parse_jit_tracing_start

    return parse_jit_mem_looptoken_alloc


@trace_step
def parse_jit_backend(line, state):
    if is_jit_backend_end(line):
        return parse_jit_tracing_start

    if is_jit_backend_dump_start(line):
        return parse_jit_backend_dump

    if is_jit_backend_addr_start(line):
        return parse_jit_backend_addr

    return parse_jit_backend


@trace_step
def parse_jit_backend_dump(line, state):
    if is_jit_backend_dump_end(line):
        state['log'].code_dumps.append(state['backend_dump'])
        del state['backend_dump']
        return parse_jit_tracing_start

    if 'backend_dump' not in state:
        state['backend_dump'] = []

    state['backend_dump'].append(line)

    return parse_jit_backend_dump


@trace_step
def parse_jit_backend_addr(line, state):
    if is_jit_backend_addr_end(line):
        return parse_jit_tracing_start

    return parse_jit_backend_addr


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

    if is_jit_log_opt_loop_start(line):
        return parse_jit_log_opt_loop

    if is_jit_optimize_start(line):
        return parse_jit_optimize

    if is_jit_backend_addr_start(line):
        return parse_jit_backend_addr

    if is_jit_log_rewritten_loop_start(line):
        return parse_jit_log_rewritten_loop

    if is_jit_log_short_preamble_start(line):
        return parse_jit_log_short_preamble

    if is_jit_log_opt_bridge_start(line):
        return parse_jit_log_opt_bridge

    if is_jit_mem_collect_start(line):
        return parse_jit_mem_collect

    if is_jit_mem_looptoken_alloc_start(line):
        return parse_jit_mem_looptoken_alloc

    # Start a new trace log
    if not state['log']:
        state['log'] = TraceLog()

    if is_jit_backend_start(line):
        return parse_jit_backend

    if is_jit_backend_dump_start(line):
        return parse_jit_backend_dump

    if is_jit_starting(line):
        return parse_jit_starting

    if ':' not in line or '~' not in line:
        return parse_jit_tracing_start

    # Collect the successive lines (= opcodes).
    assert line[0] != '[', line
    state['log'].raw_opcodes.append(line)

    return parse_jit_tracing_start


@trace_step
def parse_jit_summary(line, state):
    if is_jit_summary_end(line):
        return parse_start

    return parse_jit_summary


@trace_step
def parse_jit_backend_counts(line, state):
    if is_jit_backend_counts_end(line):
        return parse_start

    return parse_jit_backend_counts


@trace_step
def parse_start(line, state):
    if is_jit_tracing_start(line):
        return parse_jit_tracing_start

    if is_jit_summary_start(line):
        return parse_jit_summary

    if is_jit_backend_counts_start(line):
        return parse_jit_backend_counts

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

    logs = state['logs']

    for i, log in enumerate(logs):
        log.id = i + 1

    return logs
