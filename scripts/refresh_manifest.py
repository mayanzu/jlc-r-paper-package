"""Refresh infrastructure hashes while refusing changes to frozen numerical evidence."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def refresh():
    original=json.loads((ROOT/'audit/original_record_hashes.json').read_text(encoding='utf-8'))
    for name,h in original['files_sha256'].items():assert sha(ROOT/name)==h,name
    from source_archives import verify_source_archive
    verify_source_archive()
    entries={p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file()
        and not any(n in p.relative_to(ROOT).parts for n in ['.git','__pycache__','outputs','.venv'])
        and p.relative_to(ROOT).as_posix() not in ['audit/checksums.sha256','SNAPSHOT_MANIFEST.sha256']}
    text=''.join(h+'  '+n+'\n' for n,h in sorted(entries.items()))
    (ROOT/'audit/checksums.sha256').write_text(text,encoding='utf-8')
    (ROOT/'SNAPSHOT_MANIFEST.sha256').write_text(text+sha(ROOT/'audit/checksums.sha256')+'  audit/checksums.sha256\n',encoding='utf-8')
    print(f'Manifest: {len(entries)} files; frozen records unchanged.')

if __name__=='__main__':refresh()
