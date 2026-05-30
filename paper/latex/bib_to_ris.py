"""Convert references.bib to RIS format for EndNote import."""
import re
from pathlib import Path

BIB = Path(__file__).parent / "references.bib"
RIS = Path(__file__).parent / "CONTACT_WITHOUT_COMMITMENT_BLG.ris"

def parse_bib(text):
    entries = []
    # Find each @type{key, ... }
    pattern = re.compile(r'@(\w+)\{(\w+),(.+?)(?=\n@|\Z)', re.DOTALL)
    for m in pattern.finditer(text):
        etype, key, body = m.group(1), m.group(2), m.group(3)
        fields = {}
        # Parse key = {value} or key = "value"
        for fm in re.finditer(r'(\w+)\s*=\s*[{"](.+?)[}"](?:\s*,|\s*$)', body, re.DOTALL):
            fields[fm.group(1).lower()] = re.sub(r'\s+', ' ', fm.group(2).strip())
        fields['_type'] = etype.lower()
        fields['_key']  = key
        entries.append(fields)
    return entries

def authors_to_ris(author_str):
    # Split on ' and '
    authors = re.split(r'\s+and\s+', author_str, flags=re.IGNORECASE)
    lines = []
    for a in authors:
        a = a.strip()
        # Clean LaTeX
        a = re.sub(r'\\[a-zA-Z]+\{(.+?)\}', r'\1', a)
        lines.append(f"AU  - {a}")
    return lines

def pages_to_ris(pages):
    # "123--456" or "123-456"
    m = re.match(r'(\d+)\s*[-–]+\s*(\d+)', pages)
    if m:
        return [f"SP  - {m.group(1)}", f"EP  - {m.group(2)}"]
    return [f"SP  - {pages}"]

def clean(text):
    """Remove LaTeX commands for plain text."""
    text = re.sub(r'\$(.+?)\$', r'\1', text)
    text = re.sub(r'\\[a-zA-Z]+\{(.+?)\}', r'\1', text)
    text = re.sub(r'[{}]', '', text)
    text = text.replace('--', '-').replace('``', '"').replace("''", '"')
    return text.strip()

type_map = {
    'article':      'JOUR',
    'inproceedings':'CONF',
    'proceedings':  'CONF',
    'book':         'BOOK',
    'incollection': 'CHAP',
    'phdthesis':    'THES',
    'misc':         'GEN',
}

bib_text = BIB.read_text(encoding='utf-8')
entries = parse_bib(bib_text)

ris_lines = []
for e in entries:
    ty = type_map.get(e.get('_type', 'article'), 'JOUR')
    ris_lines.append(f"TY  - {ty}")
    ris_lines.append(f"ID  - {e['_key']}")

    if 'author' in e:
        ris_lines.extend(authors_to_ris(e['author']))
    if 'editor' in e:
        for ed in re.split(r'\s+and\s+', e['editor'], flags=re.IGNORECASE):
            ris_lines.append(f"ED  - {clean(ed)}")

    if 'title' in e:
        ris_lines.append(f"TI  - {clean(e['title'])}")
    if 'journal' in e:
        ris_lines.append(f"JO  - {clean(e['journal'])}")
    if 'booktitle' in e:
        ris_lines.append(f"BT  - {clean(e['booktitle'])}")
    if 'year' in e:
        ris_lines.append(f"PY  - {e['year']}")
    if 'volume' in e:
        ris_lines.append(f"VL  - {e['volume']}")
    if 'number' in e:
        ris_lines.append(f"IS  - {e['number']}")
    if 'pages' in e:
        ris_lines.extend(pages_to_ris(e['pages']))
    if 'doi' in e:
        doi = e['doi'].strip()
        ris_lines.append(f"DO  - {doi}")
        ris_lines.append(f"UR  - https://doi.org/{doi}")
    if 'url' in e:
        ris_lines.append(f"UR  - {e['url']}")
    if 'abstract' in e:
        ris_lines.append(f"AB  - {clean(e['abstract'])}")
    if 'publisher' in e:
        ris_lines.append(f"PB  - {clean(e['publisher'])}")
    if 'address' in e:
        ris_lines.append(f"CY  - {clean(e['address'])}")
    if 'note' in e:
        note = e['note']
        if '[VERIFY' not in note:
            ris_lines.append(f"N1  - {clean(note)}")

    ris_lines.append("ER  - ")
    ris_lines.append("")

RIS.write_text('\n'.join(ris_lines), encoding='utf-8')
print(f"Exported {len(entries)} references → {RIS.name}")
for e in entries:
    print(f"  [{e['_key']}] {e.get('author','?').split(',')[0]} {e.get('year','')}")
