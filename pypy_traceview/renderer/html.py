import re

from yattag import Doc
from jinja2 import Template

from pygments import highlight
from pygments.lexers import PythonLexer, ObjdumpLexer
from pygments.formatters import HtmlFormatter

from ..opcode import group_opcodes, indent_opcodes, Opcode
from ..ir import group_ir
from ..memoization import memoized


BG_COLORS = ['bg1', 'bg2', 'bg3', 'bg4']


def iter_opcodes(opcodes):
    for opcode in opcodes:
        if isinstance(opcode[0], list):
            yield from iter_opcodes(opcode)
        else:
            yield opcode


def build_color_map(opcodes):
    color_map = {}
    color_index = 0

    for group in iter_opcodes(opcodes):
        color = BG_COLORS[color_index]

        for opcode in group:
            color_map[opcode.id] = color

        color_index = (color_index + 1) % len(BG_COLORS)

    return color_map


@memoized
def highlight_snippet(snippet):
    return highlight(snippet, PythonLexer(), HtmlFormatter())


@memoized
def highlight_machine_code(snippet):
    return highlight(snippet, ObjdumpLexer(), HtmlFormatter())


def render_group(trace, group, color_map, dttl):
    doc, tag, text, line = dttl

    # Render the Python code snippet.
    bg_color = color_map[group[0].id]
    with tag('div', klass=bg_color):
        with tag('a', href='#t{}_o{}'.format(trace.id, group[0].id)):
            doc.asis(highlight_snippet(group[0].snippet))

    # Render the opcodes corresponding to the code snippet.
    with tag('div', klass='opcodes'):
        for opcode in group:
            with tag('div', klass='opcode'):
                line('div', opcode.name)

    # Add a comment about inlined code to improve reading control flow.
    if group[-1].is_call:
        comment = '\n# inlined from {}'
        snippet = comment.format(group[-1].method_snippet)
        doc.asis(highlight_snippet(snippet))


def render_indented_opcodes(trace, groups, color_map, dttl):
    doc, tag, text, line = dttl

    for group in groups:
        if isinstance(group[0], list):
            with tag('div', klass='indented'):
                render_indented_opcodes(trace, group, color_map, dttl)
        else:
            render_group(trace, group, color_map, dttl)


def render_ir(trace, color_map, dttl):
    doc, tag, text, line = dttl

    groups = group_ir(trace.raw_ir)
    kwargs = {}

    for group in groups:
        opcode = None

        if group[0].startswith('debug_merge_point'):
            raw_opcode = group[0].split('\'')[1]

            try:
                _, raw_opcode = raw_opcode.split(':')
                opcode = Opcode(raw_opcode)
            except ValueError:
                pass

            # Add a comment sign before the debug_merge_point() to easy
            # reading of the IR.
            assert len(group) == 1
            group[0] = '# ' + group[0]

            # Merge points do not have a color.
            if 'klass' in kwargs:
                del kwargs['klass']

        # Render the IR lines.
        with tag('div', **kwargs):
            snippet = '\n'.join(group)
            doc.asis(highlight_snippet(snippet))

        # Set color for next group.
        if opcode:
            kwargs['klass'] = color_map[opcode.id]
            kwargs['id'] = 't{}_o{}'.format(trace.id, opcode.id)
        elif 'id' in kwargs:
            del kwargs['id']


def hide_raw_instruction_bytes(code):
    # It would be preferable to hide the raw instruction bytes using objdump's
    # flag --no-show-raw-insn when disassembling the machine code. However,
    # pygments fails to highlight the output when that flag is given.
    code = re.sub(r'>[\t ]+<span class="mh">[^<]*</span>(?:(\n)|[\t ]+)',
                  '> \\1', code)
    return code


def render_machine_code(trace, color_map, dttl):
    doc, tag, text, line = dttl

    # Only display the first code dump. The others are not relevant.
    for dump in trace.code_dumps[:1]:
        kwargs = {'class': 'objdump'}

        with tag('div', **kwargs):
            code = '\n'.join(dump.code)
            code = highlight_machine_code(code)
            code = hide_raw_instruction_bytes(code)
            doc.asis(code)


def render_trace(trace, dttl):
    doc, tag, text, line = dttl

    with tag('a', href='#', onclick='toggleOpcodes(event)'):
        text('Toggle opcodes')

    # Try to indent the opcodes. On indentation failure, return a flat list of
    # the opcodes.
    try:
        indented = indent_opcodes(trace.opcodes)
    except AssertionError as e:
        print('failed to indent opcodes of trace ID', trace.id)
        indented = trace.opcodes

    groups = group_opcodes(indented)

    color_map = build_color_map(groups)

    with tag('div', klass='trace'):
        with tag('div', klass='code'):
            render_indented_opcodes(trace, groups, color_map, dttl)

        with tag('div', klass='ir'):
            render_ir(trace, color_map, dttl)

        with tag('div', klass='mc'):
            render_machine_code(trace, color_map, dttl)


def render(logs):
    assert logs

    doc, tag, text, line = dttl = Doc().ttl()

    with tag('div', klass='traces'):
        for trace in logs:
            line('h2', 'Trace #{}'.format(trace.id))
            render_trace(trace, dttl)

    html = doc.getvalue()

    highlight_style = HtmlFormatter().get_style_defs('.highlight')

    with open('templates/viewer.html') as f:
        template = Template(f.read())

    return template.render(traces=html, highlight_style=highlight_style)
