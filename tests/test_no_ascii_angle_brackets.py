"""Engine prose reaches the site as HTML, so '<Psi_P>' or '<x,y>' is parsed as a
tag and vanishes. Write the bra-ket / pairing brackets as U+27E8, U+27E9."""
import re
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src" / "metaphysica"
RX = re.compile(r"<(Psi|Phi|psi_|x,|z,|g_i |W\()")


def test_no_ascii_angle_brackets_in_engine_prose():
    bad = []
    for path in SRC.rglob("*.py"):
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if RX.search(line):
                bad.append("%s:%d" % (path.relative_to(SRC), n))
    assert not bad, bad
