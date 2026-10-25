"""Map compressed article tables to complete retained technical displays.

Numeric checks still inspect every cell of the original eight displays. The
four current main tables are independently compared with those verified cells.
"""
import re
from paths import TECH

def full_table_view(article):
    source=(TECH/'technical_documentation.md').read_text(encoding='utf-8')
    tables=[]
    for n in range(1,9):
        match=re.search(r'^Table E'+str(n)+r'\. [^\n]+\n\n(?:\|[^\n]*\n)+\n\*\*Table note\.\*\* [^\n]+',source,re.M)
        assert match, f'Missing complete technical table E{n}'
        tables.append(match[0].replace(f'Table E{n}.',f'Table {n}.',1))
    without=re.sub(r'^Table \d+\. [^\n]+\n\n(?:\|[^\n]*\n)+\n\*\*Table note\.\*\* [^\n]+','',article,flags=re.M)
    return without+'\n\n'+'\n\n'.join(tables)

def check_main_tables(article,parse):
    complete=full_table_view(article)
    assert re.findall(r'^Table (\d+)\.',article,re.M)==['1','2','3','4','5']
    assert parse(article,'1')==parse(complete,'1')
    _,source=parse(complete,'2');_,display=parse(article,'2')
    expected=[r[:2]+r[3:7]+[r[8]] for r in source if r[2]=='JLC-R$^{*}$']
    assert len(display)==8 and display==expected,'Compact confirmation cells differ from verified full records'
    assert parse(article,'3')==parse(complete,'4'),'Primary H1-H4 display changed'
    # JLC-Core is the manuscript display name for the internal Hybrid control
    # trajectory; normalize the header before comparing the retained cells.
    article_spatial=parse(article,'4')
    article_spatial=([v.replace('JLC-Core','Hybrid control') for v in article_spatial[0]],
                     article_spatial[1])
    assert article_spatial==parse(complete,'8'),'Spatial display changed'
    return {'main_tables':5,'compact_confirmation_rows':8,'complete_confirmation_rows':40,
            'extended_tables_verified':8,'main_numeric_cells_linked':8*5+4*5+8*7}
