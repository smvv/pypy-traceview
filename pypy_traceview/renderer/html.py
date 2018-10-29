from yattag import Doc
from jinja2 import Template

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

from ..opcode import group_opcodes, indent_opcodes


BG_COLORS = ['bg1', 'bg2', 'bg3', 'bg4']
last_bg_color = len(BG_COLORS) - 1


def next_bg_color():
    global last_bg_color
    last_bg_color = (last_bg_color + 1) % len(BG_COLORS)
    return BG_COLORS[last_bg_color]


def render_group(group, doc, tag, text, line):
    # Render the Python code snippet.
    bg_color = next_bg_color()
    with tag('div', klass=bg_color):
        doc.asis(highlight(group[0].snippet, PythonLexer(), HtmlFormatter()))

    # Render the opcodes corresponding to the code snippet.
    with tag('div', klass='opcodes'):
        for opcode in group:
            with tag('div', klass='opcode'):
                line('div', opcode.name)

    # Add a comment about inlined code to improve reading control flow.
    if group[-1].is_call:
        comment = '\n# inlined from {}'
        snippet = comment.format(group[-1].method_snippet)
        doc.asis(highlight(snippet, PythonLexer(), HtmlFormatter()))


def render_indented_opcodes(groups, doc, tag, text, line):
    for group in groups:
        if isinstance(group[0], list):
            with tag('div', klass='indented'):
                render_indented_opcodes(group, doc, tag, text, line)
        else:
            render_group(group, doc, tag, text, line)


def render_ir(trace, doc, tag, text, line):
    snippet = '\n'.join(trace.raw_ir)
    doc.asis(highlight(snippet, PythonLexer(), HtmlFormatter()))


def render_trace(trace, doc, tag, text, line):
    if not trace.opcodes:
        line('div', 'No opcodes found in trace.', klass='gray')
        return

    with tag('a', href='#', onclick='toggleOpcodes(event)'):
        text('Toggle opcodes')

    indented = indent_opcodes(trace.opcodes)
    groups = group_opcodes(indented)

    with tag('div', klass='trace'):
        with tag('div', klass='code'):
            render_indented_opcodes(groups, doc, tag, text, line)

        with tag('div', klass='ir'):
            render_ir(trace, doc, tag, text, line)


def render(logs):
    assert logs

    doc, tag, text, line = Doc().ttl()

    with tag('div', klass='traces'):
        for i, trace in enumerate(logs):
            line('h2', 'Trace #' + str(i + 1))

            render_trace(trace, doc, tag, text, line)

    html = doc.getvalue()

    highlight_style = HtmlFormatter().get_style_defs('.highlight')

    with open('templates/viewer.html') as f:
        template = Template(f.read())

    return template.render(traces=html, highlight_style=highlight_style)
