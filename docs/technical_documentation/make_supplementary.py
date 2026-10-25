# -*- coding: utf-8 -*-
"""Build package-only technical documentation from the legacy supplementary.md source."""
import io
import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--main-source',type=Path,required=True)
parser.add_argument('--bibliography',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
SRC=ROOT/'technical_documentation.md'
DST=args.output

WIDTHS = {
    'S1': [.24, .15, .18, .20, .17],
    'S2': [.16, .35, .43],
    'S3': [.17, .25, .18, .15, .19],
    'S4': [.09, .27, .32, .26],
    'S5': [.09, .27, .32, .26],
    'S16': [.06, .08, .12, .12, .14, .13, .27],
    'S18': [.06, .21, .12, .12, .12, .12, .15],
    'S19': [.35, .10, .09, .20, .20],
    'S20': [.06, .14, .12, .12, .34, .14],
    'S23': [.22, .27, .46],
    'S24': [.15, .06, .10, .10, .08, .10, .10, .11, .11],
    'S25': [.15, .06, .10, .10, .11, .10, .08, .10, .11],
    'S26': [.25, .10, .18, .42],
    'S27': [.13, .06, .21, .21, .10, .12, .12],
    'S28': [.13, .06, .25, .25, .12, .10],
    'S29': [.17, .13, .13, .13, .13, .13, .13],
    'S30': [.11, .07, .21, .21, .175, .175],
    'S31': [.14, .06, .1167, .1167, .1167, .1167, .1166, .1166],
    'S32': [.14, .06, .1167, .1167, .1167, .1167, .1166, .1166],
    'S33': [.06, .21, .27, .14, .27],
    'S34': [.36, .05, .295, .295],
    'S35': [.07, .17, .19, .18, .20, .19],
    'S41': [.12, .05, .18, .12, .12, .13, .14, .14],
    'S42': [.11, .05, .18, .24, .14, .25],
    'S43': [.11, .05, .18, .22, .21, .23],
    'S44': [.12, .05, .18, .12, .12, .13, .14, .14],
    'S45': [.11, .05, .18, .24, .14, .25],
    'S46': [.05,.25,.16,.19,.16,.19],
    'S48': [.12,.04,.18,.13,.14,.12,.14,.13],
    'S49': [.12,.04,.18,.13,.14,.12,.14,.13],
    'S50': [.12,.05,.25,.39,.19],
    'S51': [.07,.04,.16,.15,.15,.14,.15,.14],
    'S52': [.06,.05,.27,.42,.20],
    'S53': [.07,.12,.12,.15,.12,.14,.14,.14],
    'S62': [.14,.06,.12,.11,.12,.12,.15,.08],
    'S63': [.14,.06,.12,.11,.12,.12,.15,.08],
    'S67': [.12,.07,.16,.13,.14,.13,.13,.12],
    'S70': [.16,.24,.18,.16,.26],
    'S71': [.17,.23,.19,.16,.25],
    'S72': [.16,.40,.44],
}

source = SRC.read_text(encoding='utf-8')
subtitle = re.search(r'^subtitle: "([^"\n]+)"', source, re.M)
assert subtitle, 'subtitle metadata'
body = subprocess.run(['pandoc', str(SRC), '-f', 'markdown', '-t', 'latex', '--wrap=none', '--natbib'],
                      check=True, capture_output=True, encoding='utf-8').stdout
# Resolve every SI citation by key against the compiled main bibliography.
bbl=args.bibliography.read_text(encoding='utf-8')
keys=re.findall(r'\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}',bbl)
mapping={key:i+1 for i,key in enumerate(keys)}
def main_citation(match):
    names=[name.strip() for name in match[1].split(',')]
    assert all(n in mapping for n in names),names
    return '['+', '.join(str(mapping[n]) for n in names)+']'
body=re.sub(r'\\citep\{([^}]+)\}',main_citation,body)
body=re.sub(r'\\texttt\{([^{}]*[/][^{}]*)\}',
            lambda m:r'\nolinkurl{'+m[1].replace(r'\_','_')+'}',body)
body=re.sub(r'(?<![a-zA-Z0-9])([a-f0-9]{40,64})(?![a-zA-Z0-9])',
            lambda m:r'\nolinkurl{'+m[1]+'}',body)
body = body.replace('{\\def\\LTcaptype{none} % do not increment counter\n', '')
body = body.replace('\\end{longtable}\n}', '\\end{longtable}')
body = body.replace(r'\real{0.1429}', r'\real{0.1428}')
body = re.sub(r'\\FloatBarrier\n?', '', body)
body = body.replace('\\section{Supplementary Tables}\\label{supplementary-tables}',
                    '\\section*{Supplementary tables}')
body = body.replace('\\section{Supplementary Figures}\\label{supplementary-figures}',
                    '\\section*{Supplementary figures}')


def table_block(match):
    token, caption, raw = match.group(1), match.group(2), match.group(3)
    note = match.group(4)
    note_block = ('\n\\par\\vspace{3pt}{\\footnotesize\\raggedright\\textit{Note.} '
                  + note + '\\par}\n') if note else '\n'
    header = raw.split(r'\toprule\noalign{}', 1)[1].split(r'\midrule\noalign{}', 1)[0]
    header = re.sub(r'\\begin\{minipage\}\[b\]\{\\linewidth\}\\(?:raggedright|raggedleft|centering)\s*', '', header)
    header = header.replace(r'\end{minipage}', '').strip()
    data = raw.split(r'\endlastfoot', 1)[1].rsplit(r'\end{longtable}', 1)[0].strip()
    cols = len(re.findall(r'(?<!\\)&', header)) + 1
    widths = WIDTHS.get(token, [.9 / cols] * cols)
    assert len(widths) == cols, (token, cols)
    # Column widths must include the intercolumn padding within the page width.
    # A small rounding allowance prevents nominally full-width tables spilling.
    total = sum(widths)
    padding = 6 * (cols - 1) + .1
    spec = '@{}' + ''.join(
        r'>{\raggedright\arraybackslash}p{\dimexpr%.6f\linewidth-%.6fpt\relax}'
        % (w / total, padding * w / total) for w in widths) + '@{}'
    return ('\\begin{table}[H]\n'
            '\\caption*{Table %s. %s}\n\\centering\\small\\rmfamily\\setlength{\\tabcolsep}{3pt}\n'
            '\\begin{tabular}{%s}\n\\toprule\n%s\n\\midrule\n%s\n\\bottomrule\n'
            '\\end{tabular}%s\\end{table}' % (token, caption, spec, header, data, note_block))


body, ntables = re.subn(r'Table (S\d+)\. ([^\n]*)\n\n(\\begin\{longtable\}.*?\\end\{longtable\})'
                        r'(?:\n\n\\textbf\{Table note\.\} ([^\n]+))?',
                        table_block, body, flags=re.S)
declared_tables = re.findall(r'^Table (S\d+)\.', source, re.M)
layout = json.loads((ROOT.parent/'paper_audit/supplementary_layout.json').read_text(encoding='utf-8'))
assert declared_tables == layout['retained_tables'], declared_tables
assert len(declared_tables) == len(set(declared_tables)), 'Duplicate table identifier'
assert ntables == len(declared_tables), (ntables, declared_tables)
assert 'longtable' not in body

for label, stem in re.findall(r'!\[[^\n]+\]\(figures/([^\)]+)\.svg\)\{width=100%\}\s*\nFigure (S\d+)\.',source):
    label,stem=stem,label
    pattern = (r'\\begin\{figure\}\n\\centering\n'
               r'\\includesvg\[[^\]]*\]\{figures/' + stem + r'\.svg\}\n'
               r'\\caption\{(.*?)\}\n\\end\{figure\}\n\n')
    match = re.search(pattern, body, flags=re.S)
    assert match, label
    caption_pattern = (r'^Figure ' + label + r'\. ([^\n]+)\n\n'
                       r'(?:\\textbf\{Figure note\.\} ([^\n]+)\n\n)?')
    caption = re.search(caption_pattern, body, flags=re.M)
    assert caption, (label, 'source caption')
    note_block = ('{\\footnotesize\\raggedright\\textit{Note.} '
                  + caption[2] + '\\par}\n') if caption[2] else ''
    body = body[:match.start()] + (
        '\\begin{figure}[H]\n\\centering\n'
        '\\includegraphics[width=\\linewidth]{figures/' + stem + '.pdf}\n'
        '\\caption*{Figure ' + label + '. ' + caption[1] + '}\n'
        + note_block + '\\end{figure}\n\n') + body[match.end():]
    # Drop the duplicated plain-text caption paragraph left after the figure.
    body, dropped = re.subn(
        caption_pattern, '', body, count=1, flags=re.M)
    assert dropped == 1, label
assert r'\textbf{Figure note.}' not in body and r'\textbf{Table note.}' not in body

for a, b in [('×', r'$\times$'), ('−', '$-$'), ('Δ', r'$\Delta$'), ('µ', r'$\mu$'),
             ('·', r'$\cdot$'), ('²', r'$^2$'), ('⁴', r'$^4$'), ('–', '--'), ('—', '---'),
             ('Á', "\\'A"), ('ó', "\\'o"), ('é', "\\'e"), ('í', r'\i '), ('ú', "\\'u"),
             ('ñ', '\\~n'), ('ç', '\\c c'), ('≥', r'$\geq$'), ('≤', r'$\leq$'),
             ('±', r'$\pm$')]:
    body = body.replace(a, b)
left = sorted({ch for ch in body if ord(ch) > 127})
assert not left, [repr(c) + ':U+%04X' % ord(c) for c in left]

preamble = r'''% Standalone supplementary material build. Compile: pdflatex x2.
\documentclass[10pt,a4paper]{article}
\usepackage[margin=2.2cm]{geometry}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{booktabs,array,float}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{xurl}
\usepackage[hidelinks]{hyperref}
\hypersetup{pdfauthor={PDF_AUTHORS_PLACEHOLDER},pdftitle={Technical Documentation: SUBTITLE_PLACEHOLDER},pdfkeywords={KEYWORDS_PLACEHOLDER}}
\usepackage{caption}
\captionsetup{font=small,labelfont=bf,labelsep=quad}
\renewcommand{\arraystretch}{1.05}
\setlength{\emergencystretch}{3em}
\setcounter{secnumdepth}{0}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}

\title{\vspace{-1.2cm}\Large Technical Documentation\\[2pt]
\normalsize SUBTITLE_PLACEHOLDER}
\author{AUTHOR_BLOCK_PLACEHOLDER}
\date{}
\begin{document}
\maketitle
\vspace{-0.6cm}
'''.replace('SUBTITLE_PLACEHOLDER', subtitle[1])
main_source = args.main_source.read_text(encoding='utf-8')
authors = json.loads(re.search(r'^authors: (.+)$', main_source, re.M)[1])
affiliations = json.loads(re.search(r'^affiliations: (.+)$', main_source, re.M)[1])
letters = {entry['id']: chr(ord('a') + i) for i, entry in enumerate(affiliations)}
author_line = r'\quad '.join(a['name'] + r'\textsuperscript{' +
                            ','.join([letters[key] for key in a['affiliations']] +
                                     (['*'] if a.get('corresponding') else [])) + '}' for a in authors)
affiliation_lines = [r'\textsuperscript{' + letters[a['id']] + '}' +
                     ', '.join(a[key] for key in ['organization', 'city', 'postcode', 'state', 'country'])
                     for a in affiliations]
email_lines = [(r'\textsuperscript{*}Corresponding author: ' if a.get('corresponding') else 'E-mail: ') +
               a['name'] + r' (\href{mailto:' + a['email'] + r'}{\nolinkurl{' +
               a['email'] + '}})' for a in authors if a.get('email')]
author_block = (r'\parbox{0.96\textwidth}{\centering\normalsize ' + author_line +
                r'\\[4pt]\small ' + r'\\[2pt]'.join(affiliation_lines + email_lines) + '}')
preamble = preamble.replace('AUTHOR_BLOCK_PLACEHOLDER', author_block)
preamble = preamble.replace('PDF_AUTHORS_PLACEHOLDER', '; '.join(a['name'] for a in authors))
main_keywords = re.search(r'^\*\*Keywords:\*\* (.+)$', main_source, re.M)[1]
preamble = preamble.replace('KEYWORDS_PLACEHOLDER', main_keywords.replace(';', ','))

out = preamble + body + '\n\\end{document}\n'
DST.write_text(out, encoding='utf-8', newline='\n')
print('WROTE', DST.name, len(out), 'chars; tables', ntables)
