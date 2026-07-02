"""
Convert phosphoserine (SEP, monoanionic q=-1) to SP2 (dianionic q=-2) in the
CASEIN mature+phospho PDB.

Why: SEP in this force field keeps H3T protonated on the third phosphate
oxygen (monoanionic, -1). At milk pH (~6.7), above the second phosphate pKa
(~5.8-6.2), phosphoserine is predominantly dianionic (-2). SP2 in
charmm36-feb2026_ljpme_cgenff-5.0.ff/aminoacids.rtp is the fully deprotonated,
symmetric-oxygen dianionic patch (verified: atom charges sum to -2.00).

Transform (geometry is unchanged - only protonation/atom-naming differs):
  - drop the H3T atom line (deprotonated)
  - rename atom O3P -> OT (SP2's naming for the third phosphate oxygen)
  - rename residue SEP -> SP2

Input:  inputs_CAS/CASEIN_mature_phospho.pdb
Output: inputs_CAS/CASEIN_mature_phospho_SP2.pdb
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "inputs_CAS" / "CASEIN_mature_phospho.pdb"
OUTPUT = ROOT / "inputs_CAS" / "CASEIN_mature_phospho_SP2.pdb"

n_dropped = 0
n_renamed_atom = 0
n_renamed_res = 0

with open(INPUT) as f, open(OUTPUT, "w") as out:
    for line in f:
        if line.startswith(("ATOM", "HETATM")):
            atom_name = line[12:16].strip()
            resname = line[17:20].strip()
            if resname == "SEP":
                if atom_name == "H3T":
                    n_dropped += 1
                    continue
                if atom_name == "O3P":
                    line = line[:12] + " OT " + line[16:]
                    n_renamed_atom += 1
                line = line[:17] + "SP2" + line[20:]
                n_renamed_res += 1
        out.write(line)

print(f"Dropped {n_dropped} H3T atoms")
print(f"Renamed {n_renamed_atom} O3P -> OT")
print(f"Renamed {n_renamed_res} SEP -> SP2 atom lines")
print(f"Wrote {OUTPUT}")
