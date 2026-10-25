import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from analyze_effects import contrast, holm
import numpy as np


class AnalysisTests(unittest.TestCase):
    def test_known_factorial_polynomial(self):
        y={}
        for t in [0,1]:
            for r in [0,1]:
                for s in [0,1]:
                    y[f'A{t}{r}{s}']=2+3*t+5*r+7*s+11*t*r+13*t*s+17*r*s+19*t*r*s
        expected={'T':19.75,'R':23.75,'S':26.75,'TR':20.5,'TS':22.5,'RS':26.5,'TRS':19,'Bundle':75,'Loss_T':46,'Loss_R':52,'Loss_S':56}
        for k,v in expected.items():
            self.assertAlmostEqual(contrast(y,k),v,k)

    def test_holm_known_unsorted_values(self):
        np.testing.assert_allclose(holm([.04,.001,.03,.02]),[.06,.004,.06,.06])


if __name__=='__main__':
    unittest.main()
