from yattag import Doc
from jinja2 import Template

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

from ..opcode import group_opcodes


def render_group(group, doc, tag, text, line):
    opcode = group[0]

    # Render the Python code snippet.
    doc.asis(highlight(opcode.snippet, PythonLexer(), HtmlFormatter()))

    # Render the opcodes corresponding to the code snippet.
    with tag('div', klass='opcodes'):
        for opcode in group:
            with tag('div', klass='opcode'):
                line('div', opcode.name)


def render_trace(trace, doc, tag, text, line):
    groups = group_opcodes(trace.opcodes)

    for i, group in enumerate(groups):
        # Render the file/line anchor.
        opcode = group[0]
        title = 'in method {} on {}:{}'.format(
            opcode.method, opcode.filename, opcode.code_line
        )
        id = 'op' + str(i)

        with tag('a', id=id, klass='line-anchor', href='#' + id, title=title):
            text('#')

        render_group(group, doc, tag, text, line)


def render(logs):
    assert logs

    doc, tag, text, line = Doc().ttl()

    with tag('div', klass='traces'):
        for trace in logs:
            render_trace(trace, doc, tag, text, line)

    html = doc.getvalue()

    highlight_style = HtmlFormatter().get_style_defs('.highlight')

    with open('templates/viewer.html') as f:
        template = Template(f.read())

    return template.render(traces=html, highlight_style=highlight_style)
