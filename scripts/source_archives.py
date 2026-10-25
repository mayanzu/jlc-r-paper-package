"""Verify a public source container without treating it as the original ZIP."""
from pathlib import PurePosixPath
import hashlib,json,zipfile
from paths import ROOT

def verify_source_archive():
    record=json.loads((ROOT/'audit/source_snapshot_provenance.json').read_text(encoding='utf-8'))
    public=record['public_archive'];path=ROOT/public['path']
    assert path.resolve().is_relative_to(ROOT)
    assert hashlib.sha256(path.read_bytes()).hexdigest()==public['sha256']
    expected=record['source_members_sha256']
    assert len(expected)==public['members']==47
    with zipfile.ZipFile(path) as archive:
        assert len(archive.namelist())==len(set(archive.namelist()))
        assert set(archive.namelist())==set(expected)
        for name,digest in expected.items():
            rel=PurePosixPath(name)
            assert not rel.is_absolute() and '..' not in rel.parts and '.git' not in rel.parts and '\\' not in name
            assert hashlib.sha256(archive.read(name)).hexdigest()==digest,name
    originals=json.loads((ROOT/'audit/original_record_hashes.json').read_text(encoding='utf-8'))
    assert originals['offline_original_archives']==[record['original_archive']]
    assert record['original_archive']['sha256']!=public['sha256']
    assert record['original_archive']['original_relative_path'] not in originals['files_sha256']
    return {'public_source_members':len(expected),'git_metadata_in_public_archive':False,
            'original_container':'Preserved offline; original container bytes cannot be independently inspected from this distribution.',
            'source_payload_equivalence':'Recorded per-member SHA-256 matches the public archive.'}
