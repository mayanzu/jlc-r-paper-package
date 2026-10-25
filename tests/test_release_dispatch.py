"""Release safeguards; no performance simulation is executed."""
from pathlib import Path
import csv,json,sys,tempfile,unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import mechanisms
from paths import output_root
from source_archives import verify_source_archive

class ReleaseDispatchTests(unittest.TestCase):
    def setUp(self):
        base=output_root();base.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(prefix='dispatch_test_',dir=base)
        self.work=Path(self.temp.name).resolve()
        assert self.work.is_relative_to(base.resolve())
        self.addCleanup(self.temp.cleanup)
        self.report={'study':'mechanisms','planned_cases':120,'dry_run':True,'simulations_started':0}

    def test_public_source_archive_has_exact_payloads_without_git(self):
        result=verify_source_archive()
        self.assertEqual(result['public_source_members'],47)
        self.assertFalse(result['git_metadata_in_public_archive'])

    def test_original_imports_config_and_case_identities(self):
        result=mechanisms.inspect_study()
        self.assertEqual(result['planned_cases'],120)
        self.assertEqual(result['source_modules_verified'],18)
        self.assertTrue(result['effective_config_matches_original_provenance'])
        self.assertTrue(result['seed_case_identities_match'])

    def test_dry_run_never_dispatches_harness(self):
        with patch.object(mechanisms,'inspect_study',return_value=self.report),patch.object(mechanisms.subprocess,'run') as run:
            result=mechanisms.execute(self.work/'new',dry_run=True)
            self.assertEqual(result['simulations_started'],0)
            run.assert_not_called()

    def test_existing_output_is_rejected_before_dispatch(self):
        with patch.object(mechanisms,'inspect_study',return_value=self.report),patch.object(mechanisms.subprocess,'run') as run:
            with self.assertRaises(ValueError):mechanisms.execute(self.work)
            run.assert_not_called()

    def test_frozen_input_destination_is_rejected(self):
        with patch.object(mechanisms,'inspect_study',return_value=self.report),patch.object(mechanisms.subprocess,'run') as run:
            with self.assertRaises(ValueError):mechanisms.execute(ROOT/'data'/'forbidden_new_run')
            run.assert_not_called()

    def test_explicit_dispatch_uses_original_design_and_separate_process(self):
        out=self.work/'new'
        def fake_process(command,**kwargs):
            self.assertEqual(Path(command[2]),ROOT/'code/reproduction/mechanisms/simulation/run_strengthening.py')
            self.assertEqual(Path(command[command.index('--design')+1]),ROOT/'code/results/strengthening/floor/design.json')
            self.assertEqual(Path(command[command.index('--output')+1]),out)
            self.assertEqual(command[command.index('--workers')+1],'2')
            self.assertEqual(kwargs['env']['PYTHONDONTWRITEBYTECODE'],'1')
            out.mkdir()
            with (out/'metrics.csv').open('w',newline='',encoding='utf-8') as stream:
                writer=csv.writer(stream);writer.writerow(['case']);writer.writerows([[i] for i in range(120)])
        with patch.object(mechanisms,'inspect_study',return_value=self.report),patch.object(mechanisms.subprocess,'run',side_effect=fake_process) as run:
            result=mechanisms.execute(out,workers=2)
            self.assertEqual(result['completed'],120)
            run.assert_called_once()

    def test_nonpositive_workers_are_rejected(self):
        with patch.object(mechanisms,'inspect_study') as inspect:
            with self.assertRaises(ValueError):mechanisms.execute(self.work/'new',workers=0)
            inspect.assert_not_called()

if __name__=='__main__':unittest.main()
