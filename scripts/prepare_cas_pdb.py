"""
Prepare CASEIN.pdb for GROMACS simulation:
  1. Trim signal peptide (residues 1-15, full-sequence numbering)
  2. Rename 5 phosphoserines (full-seq positions 30,32,33,34,50) SER -> SEP
  3. Renumber residues starting from 1 (mature protein)

Input:  inputs_CAS/CASEIN.pdb   (AlphaFold, 224 residues, full precursor)
Output: inputs_CAS/CASEIN_mature.pdb  (209 residues, phosphoserines as SEP)
"""

from pathlib import Path

ROOT = Path(__file__).parent.parent
INPUT  = ROOT / "inputs_CAS" / "CASEIN.pdb"
OUTPUT = ROOT / "inputs_CAS" / "CASEIN_mature.pdb"

# Full-precursor residue numbers to convert SER -> SEP
PHOSPHO_RESIDS = {30, 32, 33, 34, 50}
SIGNAL_PEPTIDE_END = 15   # residues 1-15 are trimmed

lines_out = []
new_resnum = 0
prev_resnum = None

with open(INPUT) as f:
    for line in f:
        # Pass through non-ATOM/HETATM records (HEADER, TITLE, REMARK, etc.)
        if not line.startswith(("ATOM  ", "HETATM")):
            if line.startswith("END"):
                break
            lines_out.append(line)
            continue

        # PDB columns: resSeq is cols 23-26 (1-indexed), resName is cols 18-20
        resnum = int(line[22:26].strip())

        # Skip signal peptide
        if resnum <= SIGNAL_PEPTIDE_END:
            continue

        # Track residue number changes for renumbering
        if resnum != prev_resnum:
            new_resnum += 1
            prev_resnum = resnum

        # Rename phosphoserines
        resname = line[17:20].strip()
        if resnum in PHOSPHO_RESIDS:
            if resname != "SER":
                print(f"WARNING: expected SER at position {resnum}, found {resname}")
            line = line[:17] + "SEP" + line[20:]

        # Renumber residue (cols 23-26, right-justified, width 4)
        line = line[:22] + f"{new_resnum:4d}" + line[26:]
        lines_out.append(line)

lines_out.append("END\n")

with open(OUTPUT, "w") as f:
    f.writelines(lines_out)

print(f"Done. {new_resnum} residues written to {OUTPUT}")
print(f"Phosphoserines at original positions: {sorted(PHOSPHO_RESIDS)}")
print(f"  -> mature positions: {sorted(p - SIGNAL_PEPTIDE_END for p in PHOSPHO_RESIDS)}")
