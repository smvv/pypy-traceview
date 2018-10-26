from yattag import Doc
from jinja2 import Template

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter


def group_opcodes(opcodes):
    if not opcodes:
        return []

    groups = []

    last = opcodes[0]
    group = [last]

    for opcode in opcodes[1:]:
        if opcode.code_line == last.code_line:
            group.append(opcode)
        else:
            assert group
            groups.append(group)
            group = [opcode]
            last = opcode

    if group:
        groups.append(group)

    assert sum(map(len, groups)) == len(opcodes)

    return groups


def render_trace(trace, doc, tag, text, line):
    groups = group_opcodes(trace.opcodes)

    for group in groups:
        opcode = group[0]

        # Render the file/line anchor.
        id = '{}L{}'.format(opcode.filename, opcode.code_line)
        tooltip = 'in method {} on {}:{}'.format(
            opcode.method, opcode.filename, opcode.code_line
        )

        with tag('a', id=id, klass='line-anchor', href='#' + id,
                 tooltip=tooltip):
            text('#')

        # Render the Python code snippet.
        doc.asis(highlight(opcode.snippet, PythonLexer(), HtmlFormatter()))

        # Render the opcodes corresponding to the code snippet.
        with tag('div', klass='opcodes'):
            for opcode in group:
                with tag('div', klass='opcode'):
                    line('div', opcode.name)


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
