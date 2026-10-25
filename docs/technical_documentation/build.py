"""Compile package-only technical documentation into the package directory."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys
import pymupdf

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(command,cwd):
    r=subprocess.run(command,cwd=cwd,capture_output=True,text=True,encoding='utf-8',errors='replace')
    if r.returncode:raise RuntimeError(r.stdout+r.stderr)
    return r.stdout+r.stderr
def build(stamp,main_source,bibliography,work,archive):
    work=Path(work);work.mkdir(parents=True,exist_ok=False)
    run([sys.executable,'-B',str(HERE/'make_supplementary.py'),'--main-source',str(main_source),'--bibliography',str(bibliography),'--output',str(work/'supplementary.tex')],work)
    command=['pdflatex','-interaction=nonstopmode','-halt-on-error','-file-line-error','supplementary.tex']
    run(command,work);run(command,work)
    log=(work/'supplementary.log').read_text(encoding='utf-8',errors='replace')
    bad=[line for line in log.splitlines() if re.search(r'(undefined|multiply defined|Overfull \\)',line,re.I)]
    assert not bad,bad
    for old in HERE.glob('technical_documentation_*.pdf'):
        archive=Path(archive);archive.mkdir(parents=True,exist_ok=True);assert not (archive/old.name).exists()
        shutil.move(str(old),str(archive/old.name))
    pdf=HERE/f'technical_documentation_{stamp}.pdf';shutil.copyfile(work/'supplementary.pdf',pdf)
    with pymupdf.open(pdf) as d:pages=len(d)
    record={'filename_timestamp':stamp,'package_relative_path':pdf.relative_to(ROOT).as_posix(),'sha256':sha(pdf),'pages':pages,'source_sha256':sha(HERE/'technical_documentation.md'),'role':'Package-only technical documentation'}
    (HERE/'build_manifest.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    return record
